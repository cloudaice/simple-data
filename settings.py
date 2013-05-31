#-*-coding: utf-8 -*-
from tornado.options import define
import logging as logs


define("port", default=8000)

define("debug", True)

define("logger", logs.getLogger("Tornado-data"))

define("api_url", "https://api.github.com")

define("contribution_url",
       lambda user: "https://github.com/users/" + user + "/contributions_calendar_data")

city_list = [
    "heilongjiang", "jilin", "liaoning", "hebei", "shandong", "jiangsu", "zhejiang", "anhui",
    "henan", "shanxi", "shaanxi", "gansu", "hubei", "jiangxi", "fujian", "hunan", "guizou",
    "sichuan", "yunnan", "qinghai", "hainan", "shanghai", "chongqing", "tianjin", "beijing", "ningxia",
    "neimenggu", "guangxi", "xinjiang", "xizang", "guangdong", "xianggang", "taiwan", "aomen"]

define("city_list", city_list)

country_list = [
    'United Arab Emirates', 'Afghanistan', 'Albania', 'Armenia', 'Angola', 'Argentina', 'Austria',
    'Australia', 'Azerbaijan', 'Bosnia and Herzegovina', 'Bangladesh', 'Belgium', 'Burkina Faso',
    'Bulgaria', 'Burundi', 'Benin', 'Brunei Darussalam', 'Plurinational State of Bolivia', 'Brazil',
    'Bhutan', 'Botswana', 'Belarus', 'Belize', 'Canada', 'The Democratic Republic of the Congo',
    'Central African Republic', 'Congo', 'Switzerland', 'Ivory Coast', 'Chile', 'Cameroon', 'China',
    'Colombia', 'Costa Rica', 'Cuba', 'Cyprus', 'Czech Republic', 'Germany', 'Djibouti', 'Denmark',
    'Dominican Republic', 'Algeria', 'Ecuador', 'Estonia', 'Egypt', 'Western Sahara', 'Eritrea',
    'Spain', 'Ethiopia', 'Finland', 'Fiji', 'Falkland Islands (Malvinas)', 'France', 'Gabon',
    'United Kingdom', 'Georgia', 'French Guiana', 'Ghana', 'Greenland', 'Gambia', 'Guinea',
    'Equatorial Guinea', 'Greece', 'Guatemala', 'Guinea-Bissau', 'Guyana', 'Honduras', 'Croatia',
    'Haiti', 'Hungary', 'Indonesia', 'Ireland', 'Israel', 'India', 'Iraq', 'Islamic Republic of Iran',
    'Iceland', 'Italy', 'Jamaica', 'Jordan', 'Japan', 'Kenya', 'Kyrgyzstan', 'Cambodia',
    'Democratic People\u2019s Republic of Korea', 'Republic of Korea', 'Kuwait', 'Kazakhstan',
    'Lao People\u2019s Democratic Republic', 'Lebanon', 'Sri Lanka', 'Liberia', 'Lesotho', 'Lithuania',
    'Luxembourg', 'Latvia', 'Libyan Arab Jamahiriya', 'Morocco', 'Republic of Moldova', 'Madagascar',
    'The Former Yugoslav Republic of Macedonia', 'Mali', 'Myanmar', 'Mongolia', 'Mauritania', 'Malawi',
    'Mexico', 'Malaysia', 'Mozambique', 'Namibia', 'New Caledonia', 'Niger', 'Nigeria', 'Nicaragua',
    'Netherlands', 'Norway', 'Nepal', 'New Zealand', 'Oman', 'Panama', 'Peru', 'Papua New Guinea',
    'Philippines', 'Pakistan', 'Poland', 'Puerto Rico', 'Occupied Palestinian Territory', 'Portugal',
    'Paraguay', 'Qatar', 'Romania', 'Serbia', 'Russian Federation', 'Rwanda', 'Saudi Arabia',
    'Solomon Islands', 'Sudan', 'Sweden', 'Svalbard and Jan Mayen', 'Slovakia', 'Sierra Leone',
    'Senegal', 'Somalia', 'Suriname', 'El Salvador', 'Syrian Arab Republic', 'Swaziland', 'Chad',
    'Togo', 'Thailand', 'Tajikistan', 'Timor-Leste', 'Turkmenistan', 'Tunisia', 'Turkey',
    'Province of China Taiwan', 'United Republic of Tanzania', 'Ukraine', 'Uganda', 'United States',
    'Uruguay', 'Uzbekistan', 'Bolivarian Republic of Venezuela', 'Viet Nam', 'Vanuatu', 'Yemen',
    'South Africa', 'Zambia', 'Zimbabwe']

define("country_list", country_list)

country_code_list = [
    "AE", "AF", "AL", "AM", "AO", "AR", "AT", "AU", "AZ", "BA", "BD", "BE", "BF", "BG", "BI", "BJ",
    "BN", "BO", "BR", "BT", "BW", "BY", "BZ", "CA", "CD", "CF", "CG", "CH", "CI", "CL", "CM", "CN",
    "CO", "CR", "CU", "CY", "CZ", "DE", "DJ", "DK", "DO", "DZ", "EC", "EE", "EG", "EH", "ER", "ES",
    "ET", "FI", "FJ", "FK", "FR", "GA", "GB", "GE", "GF", "GH", "GL", "GM", "GN", "GQ", "GR", "GT",
    "GW", "GY", "HN", "HR", "HT", "HU", "ID", "IE", "IL", "IN", "IQ", "IR", "IS", "IT", "JM", "JO",
    "JP", "KE", "KG", "KH", "KP", "KR", "KW", "KZ", "LA", "LB", "LK", "LR", "LS", "LT", "LU", "LV",
    "LY", "MA", "MD", "MG", "MK", "ML", "MM", "MN", "MR", "MW", "MX", "MY", "MZ", "NA", "NC", "NE",
    "NG", "NI", "NL", "NO", "NP", "NZ", "OM", "PA", "PE", "PG", "PH", "PK", "PL", "PR", "PS", "PT",
    "PY", "QA", "RO", "RS", "RU", "RW", "SA", "SB", "SD", "SE", "SJ", "SK", "SL", "SN", "SO", "SR",
    "SV", "SY", "SZ", "TD", "TG", "TH", "TJ", "TL", "TM", "TN", "TR", "TW", "TZ", "UA", "UG", "US",
    "UY", "UZ", "VE", "VN", "VU", "YE", "ZA", "ZM", "ZW"]

define("country_code_list", country_code_list)

define("location_map_gist", "/gists/5677947")

define("world_location_map_gist", "/gists/5681176")
