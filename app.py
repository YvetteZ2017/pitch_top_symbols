import sys


class PitchVolume:
    def __init__(self, f_n, top_num):
        """
        :param f_n: file name
        :param top_num: number of top symbols needed
        """
        self.orders = dict()
        self.volume = dict()
        self.file_name = f_n
        self.top_number = top_num

    def calculate_volume(self):
        with open(self.file_name) as f:
            for line in f:
                message_type = line[9]
                order_id = line[10:22]

                if message_type == 'A':
                    shares = int(line[23:29])
                    stock_symbol = line[29:35]
                    price = line[35:45]
                    self.add_order(order_id, shares, stock_symbol, price)

                elif message_type == 'E':
                    shares = int(line[22:28])
                    self.execute_order(order_id, shares)

                elif message_type == 'X':
                    shares = int(line[22:28])
                    self.cancel_order(order_id, shares)

                elif message_type == 'P':
                    shares = int(line[23:29])
                    stock_symbol = line[29:35]
                    price = line[35:45]
                    self.trade(order_id, shares, stock_symbol, price)

        return self.find_top_symbols()

    def add_order(self, order_id, shares, stock_symbol, price):
        """
        Add newly accepted visible order to self.order, with key=OrderID

        """
        if order_id in self.orders:
            raise Exception('While adding new orders, order_id already exists: ', order_id)

        self.orders[order_id] = {
            'stock_symbol': stock_symbol,
            'shares': shares,
            'price': price
        }

    def execute_order(self, order_id, shares):
        """
        Remove executed shares from added orders (self.order)
        Add executed shares to volume record (self.volume) with key=Stock_Symbol

        """
        if order_id not in self.orders:
            raise Exception('Order does not exist while trying to execute an order: ', order_id)

        added_shares = self.orders[order_id]['shares']
        symbol = self.orders[order_id]['stock_symbol']
        if shares > added_shares:
            raise Exception('Executed shares more than added: ', order_id)
        if shares == added_shares:
            del self.orders[order_id]
        else:
            self.orders[order_id]['shares'] -= shares

        if symbol in self.volume:
            self.volume[symbol] += shares
        else:
            self.volume[symbol] = shares

    def cancel_order(self, order_id, shares):
        """
        Remove added order from self.order

        """
        if order_id not in self.orders:
            raise Exception('Order does not exist while trying to cancel an order: ', order_id)

        added_shares = self.orders[order_id]['shares']
        if shares > added_shares:
            raise Exception('Cancelled shares more than added: ', order_id)
        if shares == added_shares:
            del self.orders[order_id]
        else:
            self.orders[order_id]['shares'] -= shares
            if self.orders[order_id]['shares'] == 0:
                del self.orders[order_id]

    def trade(self, order_id, shares, stock_symbol, price):
        """
        Execute non-displayed orders, add shares directly to self.volume

        """
        if order_id in self.orders:
            raise Exception('Order_ID from trading message already exists in order_records')
        else:
            if stock_symbol in self.volume:
                self.volume[stock_symbol] += shares
            else:
                self.volume[stock_symbol] = shares

    def find_top_symbols(self):
        """
        Sort the volume record, find the top 10 frequent stock symbols

        """
        symbols = self.volume
        sorted_list = sorted(symbols.items(), key=lambda x: x[1], reverse=True)[:self.top_number]
        with open('Top_Volumes', 'w+') as f:
            for i in sorted_list:
                f.write(i[0] + str(i[1]) + '\n')
        return sorted_list


if __name__ == "__main__":
    top_number = 10
    if len(sys.argv) > 2:
        top_number = int(sys.argv[2])
    file_name = sys.argv[1]
    test = PitchVolume(file_name, top_number)
    test.calculate_volume()
