#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <ctype.h>
#include <curl/curl.h>
#include <json-c/json.h>

#define MAX_SYMBOLS 15000
#define MAX_SYMBOL_LENGTH 16
#define MAX_URL_LENGTH 65536
#define MAX_HTML_SIZE 4194304

typedef struct {
    char *memory;
    size_t size;
} MemoryStruct;

typedef struct {
    char symbol[MAX_SYMBOL_LENGTH];
    double price;
    double day_close;
    double percent;
    double gradient_full;
    double gradient_recent;
    double gradient_change;
    int volume;
    int volume_change;
    int trades;
    int trades_change;
} StockResult;

typedef struct {
    char symbol[MAX_SYMBOL_LENGTH];
    double gradient_recent;
    int volume;
    int trades;
} StockCache;

StockCache g_cache[MAX_SYMBOLS];
int g_cache_count = 0;

static size_t WriteMemoryCallback(void *contents, size_t size, size_t nmemb, void *userp) {
    size_t realsize = size * nmemb;
    MemoryStruct *mem = (MemoryStruct *)userp;

    char *ptr = realloc(mem->memory, mem->size + realsize + 1);
    if (!ptr) return 0;

    mem->memory = ptr;
    memcpy(&(mem->memory[mem->size]), contents, realsize);
    mem->size += realsize;
    mem->memory[mem->size] = 0;

    return realsize;
}

int is_premarket(struct tm *current_time) {
    int hour = current_time->tm_hour;
    int minute = current_time->tm_min;
    return (hour >= 4 && hour < 9) || (hour == 9 && minute < 30);
}

void init_cache_from_file() {
    FILE *file = fopen("previous_results.json", "r");
    if (!file) return;

    fseek(file, 0, SEEK_END);
    long file_size = ftell(file);
    fseek(file, 0, SEEK_SET);

    char *buffer = malloc(file_size + 1);
    if (!buffer) {
        fclose(file);
        return;
    }

    size_t bytes_read = fread(buffer, 1, file_size, file);
    if (bytes_read < (size_t)file_size) {
        fprintf(stderr, "Warning: Could not read entire file\n");
    }
    buffer[bytes_read] = '\0';
    fclose(file);

    struct json_object *json = json_tokener_parse(buffer);
    free(buffer);
    if (!json) return;

    struct json_object_iterator it = json_object_iter_begin(json);
    struct json_object_iterator itEnd = json_object_iter_end(json);

    while (!json_object_iter_equal(&it, &itEnd) && g_cache_count < MAX_SYMBOLS) {
        const char *symbol = json_object_iter_peek_name(&it);
        struct json_object *val = json_object_iter_peek_value(&it);
        
        struct json_object *gradient_obj = NULL;
        struct json_object *volume_obj = NULL;
        struct json_object *trades_obj = NULL;
        
        json_object_object_get_ex(val, "gradient_recent", &gradient_obj);
        json_object_object_get_ex(val, "volume", &volume_obj);
        json_object_object_get_ex(val, "trades", &trades_obj);
        
        if (gradient_obj && volume_obj && trades_obj) {
            strncpy(g_cache[g_cache_count].symbol, symbol, MAX_SYMBOL_LENGTH - 1);
            g_cache[g_cache_count].symbol[MAX_SYMBOL_LENGTH - 1] = '\0';
            g_cache[g_cache_count].gradient_recent = json_object_get_double(gradient_obj);
            g_cache[g_cache_count].volume = json_object_get_int(volume_obj);
            g_cache[g_cache_count].trades = json_object_get_int(trades_obj);
            g_cache_count++;
        }
        
        json_object_iter_next(&it);
    }
    
    json_object_put(json);
}

void save_cache_to_file() {
    struct json_object *json = json_object_new_object();
    
    for (int i = 0; i < g_cache_count; i++) {
        struct json_object *item = json_object_new_object();
        
        json_object_object_add(item, "gradient_recent", json_object_new_double(g_cache[i].gradient_recent));
        json_object_object_add(item, "volume", json_object_new_int(g_cache[i].volume));
        json_object_object_add(item, "trades", json_object_new_int(g_cache[i].trades));
        
        json_object_object_add(json, g_cache[i].symbol, item);
    }
    
    const char *json_str = json_object_to_json_string_ext(json, JSON_C_TO_STRING_PRETTY);
    
    FILE *file = fopen("previous_results.json", "w");
    if (file) {
        fprintf(file, "%s", json_str);
        fclose(file);
    }
    
    json_object_put(json);
}

void update_cache(const char *symbol, double gradient_recent, int volume, int trades) {
    for (int i = 0; i < g_cache_count; i++) {
        if (strcmp(g_cache[i].symbol, symbol) == 0) {
            g_cache[i].gradient_recent = gradient_recent;
            g_cache[i].volume = volume;
            g_cache[i].trades = trades;
            return;
        }
    }
    
    if (g_cache_count < MAX_SYMBOLS) {
        strncpy(g_cache[g_cache_count].symbol, symbol, MAX_SYMBOL_LENGTH - 1);
        g_cache[g_cache_count].symbol[MAX_SYMBOL_LENGTH - 1] = '\0';
        g_cache[g_cache_count].gradient_recent = gradient_recent;
        g_cache[g_cache_count].volume = volume;
        g_cache[g_cache_count].trades = trades;
        g_cache_count++;
    }
}

void get_cached_values(const char *symbol, double *gradient_recent, int *volume, int *trades) {
    for (int i = 0; i < g_cache_count; i++) {
        if (strcmp(g_cache[i].symbol, symbol) == 0) {
            *gradient_recent = g_cache[i].gradient_recent;
            *volume = g_cache[i].volume;
            *trades = g_cache[i].trades;
            return;
        }
    }
    
    *gradient_recent = 0.0;
    *volume = 0;
    *trades = 0;
}

char **read_symbol_list(const char *filename, int *num_symbols) {
    FILE *file = fopen(filename, "r");
    if (!file) {
        fprintf(stderr, "Failed to open symbol list file: %s\n", filename);
        return NULL;
    }
    
    int count = 0;
    char buffer[256];
    while (fgets(buffer, sizeof(buffer), file) && count < MAX_SYMBOLS) {
        if (strlen(buffer) > 0) {
            char *token = strtok(buffer, " \t\r\n");
            if (token && strlen(token) > 0 && strlen(token) < MAX_SYMBOL_LENGTH - 1) {
                count++;
            }
        }
    }
    
    if (count == 0) {
        fprintf(stderr, "No valid symbols found in file: %s\n", filename);
        fclose(file);
        return NULL;
    }
    
    char **symbols = calloc(count, sizeof(char *));
    if (!symbols) {
        fprintf(stderr, "Memory allocation failed for symbol array\n");
        fclose(file);
        return NULL;
    }
    
    rewind(file);
    
    int i = 0;
    while (fgets(buffer, sizeof(buffer), file) && i < count) {
        buffer[strcspn(buffer, "\r\n")] = 0;
        
        char *token = strtok(buffer, " \t");
        if (token && strlen(token) > 0 && strlen(token) < MAX_SYMBOL_LENGTH - 1) {
            symbols[i] = calloc(MAX_SYMBOL_LENGTH, 1);
            if (!symbols[i]) {
                fprintf(stderr, "Memory allocation failed for symbol %d\n", i);
                continue;
            }
            
            strncpy(symbols[i], token, MAX_SYMBOL_LENGTH - 1);
            symbols[i][MAX_SYMBOL_LENGTH - 1] = '\0';
            
            for (int j = 0; symbols[i][j]; j++) {
                symbols[i][j] = toupper((unsigned char)symbols[i][j]);
            }
            
            i++;
        }
    }
    
    fclose(file);
    *num_symbols = i;
    
    if (i == 0) {
        fprintf(stderr, "No valid symbols loaded\n");
        free(symbols);
        return NULL;
    }
    
    return symbols;
}

void free_symbol_list(char **symbols, int num_symbols) {
    if (!symbols) return;
    
    for (int i = 0; i < num_symbols; i++) {
        if (symbols[i]) {
            free(symbols[i]);
        }
    }
    free(symbols);
}

int cmp_stocks_by_trades(const void *a, const void *b) {
    return ((StockResult*)b)->trades - ((StockResult*)a)->trades;
}

void generate_html(StockResult *results, int num_results, const char *timestamp, const char *timezone_abbr, char *html_buffer) {
    size_t row_buffer_size = 1024;
    size_t table_buffer_size = row_buffer_size * (num_results + 1);
    
    char *table_buffer = malloc(table_buffer_size);
    if (!table_buffer) {
        fprintf(stderr, "Failed to allocate memory for table buffer\n");
        return;
    }
    
    table_buffer[0] = '\0';
    
    for (int i = 0; i < num_results; i++) {
        char row[row_buffer_size];
        char row_class[32] = "";
        
        if (results[i].trades > 1000) {
            strncpy(row_class, "high-trades", 31);
            row_class[31] = '\0';
        }
        
        int chars_written = snprintf(row, row_buffer_size,
                "<tr class=\"%s\">"
                "<td><a href=\"https://finance.yahoo.com/quote/%s\" target=\"_blank\">%s</a></td>"
                "<td>%.3f</td>"
                "<td>%.3f</td>"
                "<td data-order=\"%.1f\">%.1f%%</td>"
                "<td>%.1f</td>"
                "<td>%.1f</td>"
                "<td>%d</td>"
                "<td>%d</td>"
                "<td>%.1f</td>"
                "<td>%d</td>"
                "<td>%d</td>"
                "</tr>\n",
                row_class,
                results[i].symbol, results[i].symbol,
                results[i].price,
                results[i].day_close,
                results[i].percent, results[i].percent,
                results[i].gradient_full,
                results[i].gradient_recent,
                results[i].volume,
                results[i].trades,
                results[i].gradient_change,
                results[i].volume_change,
                results[i].trades_change
        );
        
        if (chars_written < 0 || chars_written >= (int)row_buffer_size) {
            fprintf(stderr, "Row buffer too small for stock %s\n", results[i].symbol);
            continue;
        }
        
        if (strlen(table_buffer) + strlen(row) >= table_buffer_size) {
            fprintf(stderr, "Table buffer overflow prevented\n");
            break;
        }
        
        strcat(table_buffer, row);
    }
    
    int html_result = snprintf(html_buffer, MAX_HTML_SIZE,
            "<!DOCTYPE html>\n"
            "<html>\n"
            "<head>\n"
            "    <meta charset=\"utf-8\">\n"
            "    <meta http-equiv=\"refresh\" content=\"60\">\n"
            "    <title>Stock Metrics %s %s</title>\n"
            "    <script type=\"text/javascript\" src=\"https://code.jquery.com/jquery-3.5.1.min.js\"></script>\n"
            "    <script type=\"text/javascript\" src=\"https://cdn.datatables.net/1.11.5/js/jquery.dataTables.min.js\"></script>\n"
            "    <link rel=\"stylesheet\" type=\"text/css\" href=\"https://cdn.datatables.net/1.11.5/css/jquery.dataTables.css\">\n"
            "    <style>\n"
            "        html.loading {\n"
            "            visibility: hidden;\n"
            "        }\n"
            "        body {\n"
            "            font-family: Arial, sans-serif;\n"
            "            background-color: #000;\n"
            "            color: #fff;\n"
            "            margin: 20px;\n"
            "            padding: 20px;\n"
            "        }\n"
            "        .container {\n"
            "            max-width: 1200px;\n"
            "            margin: 0 auto;\n"
            "        }\n"
            "        h1 {\n"
            "            color: #fff;\n"
            "            border-bottom: 2px solid #333;\n"
            "            padding-bottom: 10px;\n"
            "        }\n"
            "        table.dataTable,\n"
            "        .dataTables_wrapper,\n"
            "        .dataTables_wrapper tbody,\n"
            "        .dataTables_wrapper tbody tr,\n"
            "        .dataTables_wrapper tbody td {\n"
            "            background-color: #000 !important;\n"
            "            color: #fff !important;\n"
            "        }\n"
            "        .dataTables_wrapper thead th {\n"
            "            background-color: #1a1a1a !important;\n"
            "            color: #fff !important;\n"
            "            font-weight: bold;\n"
            "            border: 1px solid #333;\n"
            "            cursor: pointer;\n"
            "            padding: 8px;\n"
            "        }\n"
            "        .dataTables_wrapper td {\n"
            "            border: 1px solid #333;\n"
            "            padding: 8px;\n"
            "        }\n"
            "        .dataTables_wrapper tbody tr:hover td {\n"
            "            background-color: #1a1a1a !important;\n"
            "        }\n"
            "        .dataTables_wrapper td:not(:first-child) {\n"
            "            text-align: right !important;\n"
            "        }\n"
            "        a {\n"
            "            color: #4a9eff;\n"
            "            text-decoration: none;\n"
            "        }\n"
            "        a:hover {\n"
            "            color: #66b3ff;\n"
            "            text-decoration: underline;\n"
            "        }\n"
            "        .dataTables_wrapper .dataTables_length,\n"
            "        .dataTables_wrapper .dataTables_filter,\n"
            "        .dataTables_wrapper .dataTables_info,\n"
            "        .dataTables_wrapper .dataTables_paginate {\n"
            "            color: #fff !important;\n"
            "            margin: 10px 0;\n"
            "        }\n"
            "        .dataTables_wrapper label {\n"
            "            color: #fff !important;\n"
            "        }\n"
            "        .dataTables_wrapper .dataTables_info {\n"
            "            color: #fff !important;\n"
            "            padding: 10px 0;\n"
            "        }\n"
            "        .dataTables_wrapper .dataTables_paginate .paginate_button {\n"
            "            color: #fff !important;\n"
            "            border: 1px solid #333;\n"
            "            background-color: #1a1a1a;\n"
            "            margin: 0 4px;\n"
            "            padding: 5px 10px;\n"
            "        }\n"
            "        .dataTables_wrapper .dataTables_paginate .paginate_button.current {\n"
            "            background-color: #2d2d2d !important;\n"
            "            color: #fff !important;\n"
            "            border-color: #666;\n"
            "        }\n"
            "        .dataTables_wrapper .dataTables_paginate .paginate_button:hover {\n"
            "            background-color: #2d2d2d !important;\n"
            "            color: #fff !important;\n"
            "        }\n"
            "        .dataTables_wrapper .dataTables_length select,\n"
            "        .dataTables_wrapper .dataTables_filter input {\n"
            "            background-color: #1a1a1a !important;\n"
            "            color: #fff !important;\n"
            "            border: 1px solid #333;\n"
            "            padding: 5px;\n"
            "            margin: 0 5px;\n"
            "        }\n"
            "        .dataTables_wrapper .dataTables_paginate .paginate_button.disabled,\n"
            "        .dataTables_wrapper .dataTables_paginate .paginate_button.disabled:hover {\n"
            "            color: #666 !important;\n"
            "            background-color: #1a1a1a !important;\n"
            "            cursor: default;\n"
            "        }\n"
            "        .dataTables_wrapper .dataTables_length select option {\n"
            "            background-color: #1a1a1a;\n"
            "            color: #fff;\n"
            "        }\n"
            "        .dataTables_filter input::placeholder {\n"
            "            color: #999;\n"
            "        }\n"
            "        .dataTables_wrapper tbody tr.high-trades td {\n"
            "            color: #00ff00 !important;\n"
            "            font-weight: bold !important;\n"
            "        }\n"
            "    </style>\n"
            "    <script type=\"text/javascript\">\n"
            "        document.documentElement.className = 'loading';\n"
            "    </script>\n"
            "</head>\n"
            "<body>\n"
            "    <div class=\"container\">\n"
            "        <h1>Stock Metrics for %s %s</h1>\n"
            "        <table id=\"stockTable\" class=\"display\">\n"
            "            <thead>\n"
            "                <tr>\n"
            "                    <th>Symbol</th>\n"
            "                    <th>Price</th>\n"
            "                    <th>Close</th>\n"
            "                    <th>%% Change</th>\n"
            "                    <th>Gradient/2</th>\n"
            "                    <th>Recent</th>\n"
            "                    <th>Volume</th>\n"
            "                    <th>Trades</th>\n"
            "                    <th>∆Gradient</th>\n"
            "                    <th>∆Volume</th>\n"
            "                    <th>∆Trades</th>\n"
            "                </tr>\n"
            "            </thead>\n"
            "            <tbody>\n"
            "%s"
            "            </tbody>\n"
            "        </table>\n"
            "    </div>\n"
            "    <script>\n"
            "        $(document).ready(function() {\n"
            "            const table = $('#stockTable').DataTable({\n"
            "                \"order\": [[7, \"desc\"]],\n"
            "                \"pageLength\": 25,\n"
            "                \"columnDefs\": [\n"
            "                    { \"type\": \"num\", \"targets\": [1,2,3,4,5,6,7,8,9,10] }\n"
            "                ]\n"
            "            });\n"
            "            document.documentElement.className = '';\n"
            "        });\n"
            "    </script>\n"
            "</body>\n"
            "</html>",
            timestamp, timezone_abbr, timestamp, timezone_abbr, table_buffer
    );
    
    if (html_result < 0 || html_result >= MAX_HTML_SIZE) {
        fprintf(stderr, "HTML buffer overflow detected\n");
    }
    
    free(table_buffer);
}

int main(int argc, char *argv[]) {
    MemoryStruct chunk = {NULL, 0};
    StockResult *results = NULL;
    int num_results = 0;
    char timestamp[32];
    char timezone_abbr[5];
    char *html_buffer = NULL;
    char *list_filename = "combined.lis";
    char **universe = NULL;
    int num_symbols = 0;
    
    chunk.memory = malloc(1);
    if (!chunk.memory) {
        fprintf(stderr, "Initial memory allocation failed\n");
        return 1;
    }
    chunk.memory[0] = '\0';
    
    html_buffer = malloc(MAX_HTML_SIZE);
    if (!html_buffer) {
        fprintf(stderr, "Memory allocation failed for HTML buffer\n");
        free(chunk.memory);
        return 1;
    }
    
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--list") == 0 && i + 1 < argc) {
            list_filename = argv[i + 1];
            i++;
        }
    }
    
    const char *api_key_id = getenv("APCA_API_KEY_ID");
    const char *secret_key_id = getenv("APCA_API_SECRET_KEY");
    
    if (!api_key_id || !secret_key_id) {
        fprintf(stderr, "Error: API keys not set in environment variables\n");
        free(chunk.memory);
        free(html_buffer);
        return 1;
    }
    
    universe = read_symbol_list(list_filename, &num_symbols);
    if (!universe || num_symbols <= 0) {
        fprintf(stderr, "Error reading symbol list: %s\n", list_filename);
        free(chunk.memory);
        free(html_buffer);
        return 1;
    }
    
    if (num_symbols > MAX_SYMBOLS) {
        fprintf(stderr, "Warning: Limiting symbols to %d (from %d)\n", MAX_SYMBOLS, num_symbols);
        num_symbols = MAX_SYMBOLS;
    }
    
    init_cache_from_file();
    
    curl_global_init(CURL_GLOBAL_ALL);
    CURL *curl = curl_easy_init();
    
    if (curl) {
        char *url_buffer = malloc(MAX_URL_LENGTH);
        if (!url_buffer) {
            fprintf(stderr, "Memory allocation failed for URL buffer\n");
            free(chunk.memory);
            free(html_buffer);
            free_symbol_list(universe, num_symbols);
            curl_global_cleanup();
            return 1;
        }
        
        strcpy(url_buffer, "https://data.alpaca.markets/v2/stocks/snapshots?symbols=");
        
        for (int i = 0; i < num_symbols; i++) {
            strcat(url_buffer, universe[i]);
            if (i < num_symbols - 1) {
                strcat(url_buffer, ",");
            }
        }
        
        struct curl_slist *headers = NULL;
        char auth_header1[128];
        char auth_header2[128];
        
        sprintf(auth_header1, "APCA-API-KEY-ID: %s", api_key_id);
        sprintf(auth_header2, "APCA-API-SECRET-KEY: %s", secret_key_id);
        
        headers = curl_slist_append(headers, "accept: application/json");
        headers = curl_slist_append(headers, auth_header1);
        headers = curl_slist_append(headers, auth_header2);
        
        curl_easy_setopt(curl, CURLOPT_URL, url_buffer);
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteMemoryCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)&chunk);
        curl_easy_setopt(curl, CURLOPT_TIMEOUT, 120L);
        
        CURLcode res = curl_easy_perform(curl);
        
        if (res != CURLE_OK) {
            fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
            free(url_buffer);
            curl_slist_free_all(headers);
            curl_easy_cleanup(curl);
            curl_global_cleanup();
            free_symbol_list(universe, num_symbols);
            free(chunk.memory);
            free(html_buffer);
            return 1;
        }
        
        free(url_buffer);
        
        time_t now;
        struct tm *gmt_time;
        time_t eastern_time;
        struct tm *est_time;
        
        time(&now);
        gmt_time = gmtime(&now);
        time_t gmt = timegm(gmt_time);
        
        int is_dst = 0;
        if (gmt_time->tm_mon > 2 && gmt_time->tm_mon < 10) {
            is_dst = 1;
        } else if (gmt_time->tm_mon == 2) {
            int second_sunday = (14 - (gmt_time->tm_wday + 7 - (gmt_time->tm_mday % 7)) % 7);
            if (gmt_time->tm_mday >= second_sunday) {
                is_dst = 1;
            }
        } else if (gmt_time->tm_mon == 10) {
            int first_sunday = (7 - (gmt_time->tm_wday + 7 - (gmt_time->tm_mday % 7)) % 7);
            if (gmt_time->tm_mday < first_sunday) {
                is_dst = 1;
            }
        }
        
        if (is_dst) {
            eastern_time = gmt - (4 * 3600);
            strcpy(timezone_abbr, "EDT");
        } else {
            eastern_time = gmt - (5 * 3600);
            strcpy(timezone_abbr, "EST");
        }
        
        est_time = gmtime(&eastern_time);
        strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", est_time);
        
        results = malloc(num_symbols * sizeof(StockResult));
        if (!results) {
            fprintf(stderr, "Memory allocation failed for results array\n");
            curl_slist_free_all(headers);
            curl_easy_cleanup(curl);
            curl_global_cleanup();
            free_symbol_list(universe, num_symbols);
            free(chunk.memory);
            free(html_buffer);
            return 1;
        }
        
        struct json_object *json_response = json_tokener_parse(chunk.memory);
        if (!json_response) {
            fprintf(stderr, "Error parsing JSON response\n");
            free(results);
            curl_slist_free_all(headers);
            curl_easy_cleanup(curl);
            curl_global_cleanup();
            free_symbol_list(universe, num_symbols);
            free(chunk.memory);
            free(html_buffer);
            return 1;
        }
        
        for (int i = 0; i < num_symbols; i++) {
            struct json_object *snapshot = NULL;
            json_object_object_get_ex(json_response, universe[i], &snapshot);
            
            if (!snapshot) continue;
            
            struct json_object *latest_trade = NULL;
            struct json_object *minute_bar = NULL;
            
            json_object_object_get_ex(snapshot, "latestTrade", &latest_trade);
            json_object_object_get_ex(snapshot, "minuteBar", &minute_bar);
            
            if (!latest_trade || !minute_bar) continue;
            
            struct json_object *min_bar_n = NULL;
            json_object_object_get_ex(minute_bar, "n", &min_bar_n);
            if (!min_bar_n) continue;
            
            int minute_trades = json_object_get_int(min_bar_n);
            if (minute_trades < 50) continue;
            
            struct json_object *trade_t = NULL;
            json_object_object_get_ex(latest_trade, "t", &trade_t);
            if (!trade_t) continue;
            
            struct json_object *trade_p = NULL;
            json_object_object_get_ex(latest_trade, "p", &trade_p);
            if (!trade_p) continue;
            
            double price_now = json_object_get_double(trade_p);
            
            struct json_object *daily_bar = NULL;
            json_object_object_get_ex(snapshot, "dailyBar", &daily_bar);
            if (!daily_bar) continue;
            
            struct json_object *daily_c = NULL;
            json_object_object_get_ex(daily_bar, "c", &daily_c);
            if (!daily_c) continue;
            
            double day_close = json_object_get_double(daily_c);
            
            struct json_object *min_bar_v = NULL;
            json_object_object_get_ex(minute_bar, "v", &min_bar_v);
            if (!min_bar_v) continue;
            
            int minute_volume = json_object_get_int(min_bar_v);
            
            double reference_price;
            
            int premarket_time = is_premarket(est_time);
            
            if (premarket_time) {
                reference_price = day_close;
            } else {
                struct json_object *prev_daily_bar = NULL;
                json_object_object_get_ex(snapshot, "prevDailyBar", &prev_daily_bar);
                if (!prev_daily_bar) continue;
                
                struct json_object *prev_daily_c = NULL;
                json_object_object_get_ex(prev_daily_bar, "c", &prev_daily_c);
                if (!prev_daily_c) continue;
                
                reference_price = json_object_get_double(prev_daily_c);
            }
            
            double percent = ((price_now - reference_price) / reference_price) * 100.0;
            double gradient_full = percent / 2.0;
            double gradient_recent = ((price_now - day_close) / day_close) * 100.0;
            
            double prev_gradient_recent;
            int prev_volume;
            int prev_trades;
            
            get_cached_values(universe[i], &prev_gradient_recent, &prev_volume, &prev_trades);
            
            strncpy(results[num_results].symbol, universe[i], MAX_SYMBOL_LENGTH - 1);
            results[num_results].symbol[MAX_SYMBOL_LENGTH - 1] = '\0';
            results[num_results].price = price_now;
            results[num_results].day_close = day_close;
            results[num_results].percent = percent;
            results[num_results].gradient_full = gradient_full;
            results[num_results].gradient_recent = gradient_recent;
            results[num_results].gradient_change = gradient_recent - prev_gradient_recent;
            results[num_results].volume = minute_volume;
            results[num_results].volume_change = minute_volume - prev_volume;
            results[num_results].trades = minute_trades;
            results[num_results].trades_change = minute_trades - prev_trades;

            update_cache(universe[i], gradient_recent, minute_volume, minute_trades);

            num_results++;
        }

        json_object_put(json_response);
        curl_slist_free_all(headers);

        if (num_results > 0) {
            printf("Total of %d stocks processed\n", num_results);

            qsort(results, num_results, sizeof(StockResult), cmp_stocks_by_trades);

            generate_html(results, num_results, timestamp, timezone_abbr, html_buffer);

            FILE *html_file = fopen("latest.html", "w");
            if (html_file) {
                fprintf(html_file, "%s", html_buffer);
                fclose(html_file);

                if (system("scp -q latest.html stockminer@www.stockminer.net:/home/71/00/8200071/public_html/latest/index.html") != 0) {
                    fprintf(stderr, "Warning: SCP command may have failed\n");
                }
                printf("Updated %s %s\n", timestamp, timezone_abbr);
            } else {
                fprintf(stderr, "Error saving HTML file\n");
            }

            save_cache_to_file();
        } else {
            fprintf(stderr, "No valid stock data found\n");
        }

        free(results);
        curl_easy_cleanup(curl);
    } else {
        fprintf(stderr, "Failed to initialize curl\n");
    }

    curl_global_cleanup();
    free_symbol_list(universe, num_symbols);
    free(chunk.memory);
    free(html_buffer);

    return 0;
}
