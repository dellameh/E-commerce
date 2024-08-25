import agentpy as ap
import numpy as np
import time


class BuyerAgent(ap.Agent):
    def setup(self):
        self.budget = np.random.uniform(1, 200)
        self.name=f"buyer {np.random.randint(1, 100)}"
        self.desired_product = np.random.choice(self.model.products)
        self.satisfied = False
        self.field='agents'
        self.pos=tuple(np.random.randint(1, 10,size=2))
        self.model.grid[self.field][self.pos].add(self.name)
        self.shopping_preferences = {
            'price_weight': round(np.random.uniform(0.5, 1.5), 3),
            'distance_weight': round(np.random.uniform(0.5, 1.5), 3)
        }
        self.product_preferences = {product: {'price_weight': np.random.uniform(0.5, 1.5), 'distance_weight': np.random.uniform(0.5, 1.5)} for product in self.model.products}

    def act(self):
        if not self.satisfied and self.budget > 0:
            sellers_with_desired_product = [seller for seller in self.model.sellers if self.desired_product in seller.product_inventory and seller.product_inventory[self.desired_product] > 0]
            if sellers_with_desired_product:
                weighted_scores = []
                print('Buyer budget:', round(self.budget, 3))
                print("Buyer position", self.pos)
                print(self.desired_product)
                print(self.shopping_preferences)
                for seller in sellers_with_desired_product:
                    price_score = 1 / (1 + (abs(self.budget - seller.prices[self.desired_product]) * self.product_preferences[self.desired_product]['price_weight']))
                    distance_score = 1 / (1 + (np.linalg.norm(tuple(map(lambda i, j: i - j, self.pos, seller.pos))) * self.product_preferences[self.desired_product]['distance_weight']))
                    total_score = price_score + distance_score
                    weighted_scores.append((seller, total_score))
                    print(f"{seller} |  Price: {round(seller.prices[self.desired_product], 3)} | Position: {np.array(seller.pos)} | Inventory: {seller.product_inventory}")

                seller, _ = max(weighted_scores, key=lambda x: x[1])
                if seller.prices[self.desired_product] <= self.budget:
                    res=seller.sell(self, self.desired_product)
                    time.sleep(2)
        
                    self.satisfied = True
                    print(f"Buyer {self} is satisfied with the purchase of {self.desired_product}. Remaining budget: {self.budget:.2f}")
                    print("---------------------------------------------------------")
                else:
                    print(f"Buyer {self} cannot afford the desired product.", '\n')

class SellerAgent(ap.Agent):
    def setup(self):
        self.name=f"seller {np.random.randint(1, 100)}"
        self.product_inventory = {product: np.random.randint(1, 10) for product in self.model.products}
        self.prices = {product: np.random.uniform(10, 50) for product in self.product_inventory}
        self.pos=tuple(np.random.randint(1, 10,size=2))
        self.field='agents'
        self.model.grid[self.field][self.pos].add(self.name)
    def sell(self, buyer, product):
        if product in self.product_inventory and self.product_inventory[product] > 0:
            self.model.record_transaction(buyer, self, product, self.prices[product])
            buyer.budget -= self.prices[product]
            self.product_inventory[product] -= 1
            print(f"Seller {self} sold {product} to Buyer {buyer} for ${self.prices[product]:.2f}. Remaining inventory: {self.product_inventory}")
        else:
            print(f"Seller {self} is out of stock for {product}.")
        return self.prices[product]

    def step(self):
        if np.random.rand() < 0.1:  # 10% chance of restocking
            self.product_inventory = {product: np.random.randint(1, 10) for product in self.model.products}
            print(f"Seller {self} restocked inventory: {self.product_inventory}")

class ECommerceMarketplace(ap.Model):
    def setup(self):
        self.grid = ap.Grid(self, (10, 10))  # 10x10 grid
        self.products = ['clothes', 'shoes', 'bag', 'glasses']
        self.buyers = ap.AgentList(self, self.p.buyer_agents, BuyerAgent)
        self.sellers = ap.AgentList(self, self.p.seller_agents, SellerAgent)
        self.transactions = []

    def record_transaction(self, buyer, seller, product, price):
        self.transactions.append({
            "buyer": buyer,
            "seller": seller,
            "product": product,
            "price": price
        })

    def step(self):
        self.buyers.act()

# Parameters
parameters = {
    'buyer_agents': 5,
    'seller_agents': 7,
}

# Create and run the simulation
model = ECommerceMarketplace(parameters)
results = model.run(steps=10)
