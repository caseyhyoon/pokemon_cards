import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd


def pokemon_generate():

    purchase_date = [
            '05/29/2024',
            '05/12/2024',
            '05/29/2024',
            '05/29/2024',
            '05/29/2024',
            '05/29/2024',
            '05/29/2024',
            '06/13/2024',
            '06/13/2024',
            '06/13/2024',
            '05/29/2024',
            '05/29/2024',
            '05/29/2024',
            '05/29/2024',
            '05/29/2024',
            '05/28/2024'
    ]

    card_name = [
            "Roaring Moon ex - 251/182 - SV04: Paradox Rift (PAR)",
            "Altaria ex - 253/182 - SV04: Paradox Rift (PAR)",
            "Mew V (Alternate Full Art) - SWSH08: Fusion Strike (SWSH08)",
            "Serena (Full Art) - SWSH12: Silver Tempest (SWSH12)",
            "Iono - 237/091 - SV: Paldean Fates (PAF)",
            "Morpeko - 206/182 - SV04: Paradox Rift (PAR)",
            "Charizard ex - 223/197 - SV03: Obsidian Flames (OBF)",
            "Hisuian Samurott VSTAR - Crown Zenith: Galarian Gallery (CRZ:GG)",
            "Mew - Crown Zenith: Galarian Gallery (CRZ:GG)",
            "Simisear VSTAR - Crown Zenith: Galarian Gallery (CRZ:GG)",
            "Gardevoir - SWSH12: Silver Tempest Trainer Gallery (SWSH12: TG)",
            "Jynx - SWSH12: Silver Tempest Trainer Gallery (SWSH12: TG)",
            "Gloom - 198/197 - SV03: Obsidian Flames (OBF)",
            "Milotic - SWSH12: Silver Tempest Trainer Gallery (SWSH12: TG)",
            "Poppy - 227/197 - SV03: Obsidian Flames (OBF)",
            "Ninetales -199/197 - SV03: Obsidian Flames (OBF)"
    ]

    purchase_price = [
        67.42,
        24.73,
        46.00,
        18.00,
        30.00,
        10.12,
        48.59,
        6.53,
        6.53,
        7.61,
        1.82,
        1.08,
        3.91,
        1.30,
        3.24,
        7.97
    ]

    supply = [
        5,
        3,
        2,
        2,
        4,
        2,
        2,
        3,
        3,
        1,
        9,
        6,
        13,
        20,
        5,
        3
    ]
    
    shipping = [
        5.00,
        5.00,
        5.00,
        0.75,
        0.75,
        0.75,
        5.00,
        0.75,
        0.75,
        0.75,
        0.75,
        0.75,
        0.75,
        0.00,
        0.75,
        0.75
    ]

    pokemon_dict = {'purchase_date': purchase_date, 'card_name': card_name, 'purchase_price': purchase_price, 'supply': supply, 'shipping': shipping}
    pokemon_df = pd.DataFrame(pokemon_dict).reset_index().rename(columns={'index': 'card_no'})

    c_file = open("cards.txt", "r")
    cards = [x.strip() for x in c_file.readlines()]
    c_file.close()

    sales_df = pd.DataFrame()

    for card in cards:
        print(card)
        # Setup ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)

        driver.get(card)

        # Wait for the page to load (you might need to adjust the sleep time)
        time.sleep(5)

        # Extract the product title
        title_element = driver.find_element(By.CSS_SELECTOR, "h1.product-details__name")
        title = title_element.text
        print("Product Title:", title)

        # Extract the price
        price_element = driver.find_element(By.CSS_SELECTOR, "span.spotlight__price")
        price = price_element.text
        print("Price:", price)

        # Click "View More Data" button
        view_more_button = driver.find_element(By.CSS_SELECTOR, "div.modal__activator")
        view_more_button.click()
        time.sleep(5)

        # Load all possible data points
        try:
            while True:
                load_more_button = driver.find_element(By.CSS_SELECTOR, "div.sales-history-snapshot__load-more-container")
                load_more_button.click()
                time.sleep(2)
        except:
            print("No more to load")

        col = ["date", "condition", "quantity", "price"]

        sales_dict = {
            x: [y.text for y in driver.find_elements(By.CSS_SELECTOR, "."+x)] for x in col
        }

        limit = min([len(sales_dict[x]) for x in col])

        for x in col:
            sales_dict[x] = sales_dict[x][:limit]

        sales = pd.DataFrame(sales_dict)
        sales['card_name'] = title
        pokemon_df.loc[pokemon_df['card_name'] == title, 'curr_sale_price'] = price.replace('$','')

        sales_df = pd.concat([sales_df, sales])
        #Close the driver
        driver.quit()
    
    sales_df.loc[sales_df['quantity'] == '', 'quantity'] = '0'
    sales_df['quantity'] = sales_df['quantity'].astype(int)
    pokemon_df.loc[pokemon_df['curr_sale_price'] == '', 'curr_sale_price'] = '0'
    pokemon_df['curr_sale_price'] = pokemon_df['curr_sale_price'].astype(float)    
    pokemon_df['fees'] = pokemon_df['curr_sale_price'] * 0.13
    pokemon_df['break_even'] = pokemon_df['curr_sale_price'] - pokemon_df['shipping'] - pokemon_df['fees']
    pokemon_df['buy_price'] = pokemon_df['break_even'] * 0.7
    pokemon_df['curr_pot_profit'] = (pokemon_df['break_even'] - pokemon_df['purchase_price']) * pokemon_df['supply']
    pokemon_df['total_pp_spent'] = pokemon_df['purchase_price'] * pokemon_df['supply']
    
    pokemon_df.to_csv('pokemon.csv', index=False)
    sales_df.to_csv('sales.csv', index=False)
    
if __name__ == "__main__":
    pokemon_generate()
