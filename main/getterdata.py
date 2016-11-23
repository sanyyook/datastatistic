from dwapii import datawiz
import datetime
import pandas as pd
from django.core.cache import cache

class GetterData():

    def __init__(self, login="", password=""):
        self.dw = datawiz.DW(login, password)
        self.client_info = None
        self.products = None
        self.shops = None
        self.sale_info_len = 0
        self.count_on_page = 20
        self.get_client_info()
        if self.client_info:
            self.getShops()

    def get_client_info(self):
        try:
            self.client_info= self.dw.get_client_info()
        except Exception:
            self.client_info = None


    def getShops(self):
        self.shops = [shop for shop in self.client_info['shops'] ]

    def show_user_info(self):
        for key, info in self.client_info.items():
            print("{}: {}".format(key, info))



    def get_cat_selInfo(self, date):
        cahe_key = "main-factor{}".format(date)
        result = cache.get(cahe_key)

        try:

            if len(result) > 0:
                return result
        except Exception:
            result = self.dw.get_categories_sale(categories=self.get_categories(),
                                             shops=self.shops,
                                             date_from=date,
                                             date_to=date,
                                             by='qty')
        cache.set(cahe_key, result, None)
        return result


    def get_salec_product(self, date, order_by):
        cahe_key = "{}{}".format(date, order_by)
        result = cache.get(cahe_key)
        try:

            if len(result) > 0:
                return result
        except Exception:
            result = self.dw.get_products_sale(shops = self.shops,
                                            date_from=date,
                                            date_to=date,
                                            interval = datawiz.DAYS,
                                            by=order_by)
        cache.set(cahe_key, result, None)
        return result



    def getMainFactors(self, date_1, date_2):

        res_1 = self.get_cat_selInfo(date_1)
        res_2 = self.get_cat_selInfo(date_2)

        if len(res_1) == 0 or len(res_2) == 0:
            return None

        factors = pd.concat([res_1.T, res_2.T], axis=1)
        factors['difference'] = factors[factors.columns[0]] - factors[factors.columns[1]]
        factors['difference-percent'] = factors['difference'] / (factors[factors.columns[1]]/100)


        ret_factor = {'date_1':date_1, 'date_2': date_2 }
        ret_factor['turnover'] = [round(q, 2 ) for  q in factors.loc['turnover']]
        ret_factor['receipts_qty'] = [round(q, 2 ) for  q in factors.loc['receipts_qty']]
        ret_factor['avg_receipt'] = [round(q, 2 ) for  q in factors.loc['avg_receipt']]
        ret_factor['qty'] = [round(q, 2 ) for  q in factors.loc['qty']]
        return ret_factor


    def get_categories(self):
        result = self.dw.get_category()
        return int(result['results'][0]['category_id'])


    def parse_date(self, date_str):
        return datetime.datetime.strptime(date_str, "%Y.%m.%d")



    def get_sale_info(self, date_1, date_2, increased=True, page=1):

        start = (page - 1) * self.count_on_page
        result_turn_1 = self.get_salec_product(date_1, "turnover")
        result_qty_1 = self.get_salec_product(date_1, "qty")

        result_turn_2 = self.get_salec_product(date_2, "turnover")
        result_qty_2 = self.get_salec_product(date_2, "qty")


        factors_qty = pd.concat([result_qty_1.T, result_qty_2.T], axis=1)
        factors_turnover = pd.concat([result_turn_1.T, result_turn_2.T], axis=1)

        factors_qty['differ_qty'] = factors_qty[factors_qty.columns[0]] - factors_qty[factors_qty.columns[1]]
        factors_turnover['differ_turnover'] = factors_turnover[factors_turnover.columns[0]] - factors_turnover[factors_qty.columns[1]]

        del factors_qty[factors_qty.columns[0]]
        del factors_qty[factors_qty.columns[0]]

        del factors_turnover[factors_turnover.columns[0]]
        del factors_turnover[factors_turnover.columns[0]]

        result_factors = pd.concat([factors_qty, factors_turnover], axis=1)

        if increased:
            res = result_factors[result_factors['differ_qty'] < 0]
        else:
            res = result_factors[result_factors['differ_qty'] > 0]

        res = res.sort_values(by='differ_qty', ascending=False)


        self.sale_info_len = len(res)
        return self.transform_data(res[start:start + self.count_on_page])


    def transform_data(self, data):

        dict = {}

        for i in data.index:
            dict[i] = {"qty ": data.loc[i].differ_qty,
                       "turnover ": data.loc[i].differ_turnover}
        return dict
