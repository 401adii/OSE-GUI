#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "driver/gpio.h"
#include "driver/uart.h"
#include "esp_timer.h"
#include "esp_log.h"

#define MAIN_TAG    "MAIN"

#define DHT_PIN     GPIO_NUM_18
#define RED_PIN     GPIO_NUM_22
#define GREEN_PIN   GPIO_NUM_23

#define DHT_DATA_SIZE_B   5U

#define UART_BAUDRATE 115200
#define UART_BUFFER_SIZE 256
#define UART_QUEUE_SIZE 10

static QueueHandle_t g_uart_queue;

/* 
 * Helper function for GPIO pin polling.
 */
static int wait_for_level(gpio_num_t pin, int level, uint32_t timeout_us)
{
    int64_t start = esp_timer_get_time();
    while(gpio_get_level(pin) != level)
    {
        if((uint32_t)(esp_timer_get_time() - start) > timeout_us)
        {
            return -1;
        }
    }
    return (int)(esp_timer_get_time() - start);
}
/*
 * Asks and reads values of humidity and temperature
 * Returns ESP_OK/ESP_ERR_TIMEOUT/ESP_ERR_INVALID_CRC
 */
static esp_err_t dht11_read(gpio_num_t pin, int *humidity, int *temperature)
{
    uint8_t data[DHT_DATA_SIZE_B] = {0};
    const uint8_t data_in_bits = DHT_DATA_SIZE_B * 8;
    /*
    * 5.2 MCU Sends out Start Signal to DHT (Figure 3, below)
    * Data Single-bus free status is at high voltage level. When the communication between MCU and
    * DHT11 begins, the programme of MCU will set Data Single-bus voltage level from high to low
    * and this process must take at least 18ms to ensure DHT’s detection of MCU's signal, then MCU
    * will pull up voltage and wait 20-40us for DHT’s response.
    */
    gpio_set_direction(pin, GPIO_MODE_OUTPUT_OD);
    gpio_set_pull_mode(pin, GPIO_PULLUP_ONLY);
    gpio_set_level(pin, 0);
    vTaskDelay(pdMS_TO_TICKS(20));

    gpio_set_level(pin, 1);
    gpio_set_direction(pin, GPIO_MODE_INPUT);

    /*
    * 5.3 DHT Responses to MCU (Figure 3, above)
    * Once DHT detects the start signal, it will send out a low-voltage-level response signal, which
    * lasts 80us. Then the programme of DHT sets Data Single-bus voltage level from low to high and
    * keeps it for 80us for DHT’s preparation for sending data.
    */
    portMUX_TYPE mux = portMUX_INITIALIZER_UNLOCKED;
    portENTER_CRITICAL(&mux);

    if(wait_for_level(pin, 0, 200) < 0)
    {
        portEXIT_CRITICAL(&mux);
        return ESP_ERR_TIMEOUT;
    }

    if(wait_for_level(pin, 1, 100) < 0)
    {
        portEXIT_CRITICAL(&mux);
        return ESP_ERR_TIMEOUT;
    }

    /*
    * When DATA Single-Bus is at the low voltage level, this means that DHT is sending the response
    * signal. Once DHT sent out the response signal, it pulls up voltage and keeps it for 80us and
    * prepares for data transmission. 
    */
    if(wait_for_level(pin, 0, 100) < 0)
    {
        portEXIT_CRITICAL(&mux);
        return ESP_ERR_TIMEOUT;
    }
    /*
    * When DHT is sending data to MCU, every bit of data begins with the 50us low-voltage-level and
    * the length of the following high-voltage-level signal determines whether data bit is "0" or "1"
    * (see Figures 4 and 5 below).
    */
    for(int i = 0; i < data_in_bits; i++)
    {
        if(wait_for_level(pin, 1, 100) < 0)
        {
            portEXIT_CRITICAL(&mux);
            return ESP_ERR_TIMEOUT;
        }
        
        /* Measure HIGH duration (26-28us = '0', 70us = '1') */
        int high_duration = wait_for_level(pin, 0, 120);
        if(high_duration < 0)
        {
            portEXIT_CRITICAL(&mux);
            return ESP_ERR_TIMEOUT;
        }

        if (high_duration > 40)
        {
            data[i / 8] |= (1 << (7 - (i % 8)));
        }
    }

    portEXIT_CRITICAL(&mux);
    /* 
    * Data format: 8bit integral RH data + 8bit decimal RH data + 8bit integral T data + 8bit decimal T
    * data + 8bit check sum. If the data transmission is right, the check-sum should be the last 8bit of
    * "8bit integral RH data + 8bit decimal RH data + 8bit integral T data + 8bit decimal T data".
    */
    uint8_t checksum = data[0] + data[1] + data[2] + data[3];
    if(checksum != data[4])
    {
        ESP_LOGE(MAIN_TAG, "Checksum error: calculated %02x != received %02X", checksum, data[4]);
        return ESP_ERR_INVALID_CRC;
    }

    *humidity = data[0];
    *temperature = data[2];
    
    return ESP_OK;
}

/*
* UART Command parsing and dispatching
*/
static void cmd_dispatcher(uint8_t *data, uint8_t data_size)
{
    int param = -1;
    int temperature = 0xFF; /* DHT11 Line pulled high if not working */
    int humidity = 0xFF;
    if(sscanf((const char *)data, "LEDG %d", &param) == 1)
    {
        if(param == 1 || param == 0)
        {
            gpio_set_level(GREEN_PIN, param);
        }
    }
    else if(sscanf((const char *)data, "LEDR %d", &param) == 1)
    {
        if(param == 1 || param == 0)
        {
            gpio_set_level(RED_PIN, param);
        }
    }
    else if(strncmp("READANDGET", (const char *)data, (size_t)data_size) == 0)
    {
        dht11_read(DHT_PIN, &humidity, &temperature);
        //transmit back over uart.
    }
}

void app_main(void)
{
    gpio_config_t gpio_conf = {
        .mode = GPIO_MODE_OUTPUT,
        .pin_bit_mask = (1ULL << RED_PIN) | (1ULL << GREEN_PIN),
        .intr_type = GPIO_INTR_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .pull_up_en = GPIO_PULLUP_DISABLE,
    };
    
    gpio_config(&gpio_conf);

    uart_config_t uart_conf = {
        .baud_rate = UART_BAUDRATE,
        .data_bits = UART_DATA_8_BITS,
        .parity = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .source_clk = UART_SCLK_DEFAULT,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
    };
    
    uart_param_config(UART_NUM_0, &uart_conf);
    uart_driver_install(UART_NUM_0, UART_BUFFER_SIZE, UART_BUFFER_SIZE, UART_QUEUE_SIZE, &g_uart_queue, 0);

    uart_event_t event = {0};
    uint8_t data[UART_BUFFER_SIZE];

    while(1)
    {
        if(xQueueReceive(g_uart_queue, &event, pdMS_TO_TICKS(1000)))
        {
            if(event.type == UART_DATA)
            {
                uint16_t bytes_read = uart_read_bytes(UART_NUM_0, data, event.size, pdMS_TO_TICKS(1000));
                if(bytes_read > 0)
                {
                    data[bytes_read] = '\0';
                    cmd_dispatcher(data, bytes_read);
                }
            }
        }
    }
}
