import functools
import json
import operator
from collections import Counter, namedtuple
from multiprocessing import Pool, cpu_count
from pprint import pprint

import requests

import xlrd

_alb_fields = [
    "title",
    "link",
    "author",
    "pubDate",
    "description",
    "creator",
    "isbn",
    "isbn13",
    "itemId",
    "priceSales",
    "priceStandard",
    "stockStatus",
    "mileage",
    "cover",
    "categoryId",
    "categoryName",
    "publisher",
    "customerReviewRank",
    "bookinfo",
]

AladinBook = namedtuple(
    "AladinBook",
    _alb_fields,
)

def new_alb(**kwargs):
    base = {f: None for f in _alb_fields}
    base.update(kwargs)
    return AladinBook(**base)

# ['version', 'title', 'link', 'pubDate', 'imageUrl', 'totalResults', 'startIndex', 'itemsPerPage', 'query', 'searchCategoryId', 'searchCategoryName', 'item']


def aladin_from_isbn13(isbn13):
    params = {
        "TTBKey": "***REMOVED***",
        "ItemId": isbn13,
        "ItemIdType": "ISBN13",
        "Output": "JS",
    }

    r = requests.get("http://www.aladin.co.kr/ttb/api/ItemLookUp.aspx", params=params)

    # try:
    #     print("strange:")
    #     print(r.text.replace(";", "")[1326])
    # except:
    #     pass

    j = json.loads(r.text.replace(";", "").replace(r"\'", "'"), strict=False)

    try:
        return new_alb(**j["item"][0])
    except KeyError:
        return None


# print(repr(aladin_from_isbn13('')))
# print(aladin_from_isbn13(0)["item"][0].keys())
# pprint(AladinBook(**aladin_from_isbn13(0)["item"][0]))


def aladin_categories():
    wb = xlrd.open_workbook("~/download/aladin_Category_CID_20200626.xls")
    ws = wb.sheet_by_index(0)
    c = {}

    for r in range(ws.nrows):
        row = list(ws.row_values(r))
        c.update({int(row[0]): (row[1], row[3], row[4])})

    return c


CATEGORIES = aladin_categories()  # {CID: (CNAME, 1thCID, 2thCID)}


LibraryBook = namedtuple(
    "LibraryBook",
    [
        "no",
        "ranking",
        "bookname",
        "authors",
        "publisher",
        "publication_year",
        "isbn13",
        "addition_symbol",
        "vol",
        "class_no",
        "loan_count",
        "bookImageURL",
    ],
)


PAGE_SIZE = 100

def a_library_high_school(page):
    # 주어진 페이저 번호의 대출 도서 목록을 가져온다.
    params = {
        "authKey": "***REMOVED***",
        "from_age": 17,
        "to_age": 19,
        "format": "json",
        "pageNo": page,
        "pageSize": PAGE_SIZE,
    }

    r = requests.get("http://data4library.kr/api/loanItemSrch", params=params)

    try:
        ds = r.json()["response"]["docs"]
    except:
        return []

    return [LibraryBook(**d["doc"]) for d in ds]


def library_high_school(n):
    whole_requests = int(n/PAGE_SIZE + 0.5) #  반올림
    with Pool(cpu_count()) as p:
        res = p.imap(a_library_high_school, range(1, whole_requests+1))
        return functools.reduce(operator.concat, res)[:n]


# def library_high_school(n):
#     # 가장 인기많은 순서대로 n개를 가져온다.
#     params = {
#         "authKey": "***REMOVED***",
#         "from_age": 17,
#         "to_age": 19,
#         "format": "json",
#     }

    # res = []
    # page_num = 1
    # cont = True

    # while cont:
    #     params["pageNo"] = page_num
    #     r = requests.get("http://data4library.kr/api/loanItemSrch", params=params)
    #     try:
    #         ds = r.json()["response"]["docs"]
    #         res.extend(ds)
    #     except:
    #         cont = False

        # if len(res) >= n:
        #     cont = False

        # page_num += 1

    # print(r.json()["response"]["resultNum"])

    # return [LibraryBook(**d["doc"]) for d in res[:n]]

def library_to_aladin(lbs):
    # TODO
    return 0

# 동시성 사용 버전의 알라딘
# def library_to_aladin(lbs):
#     # 실제로 받는 건 원래 있는 것보다 더 적을 수 도 있다.
#     with Pool(cpu_count()) as p:
#         chuncksize = int(len(lbs)/cpu_count() + 0.5) # 반올림
#         it = p.imap(aladin_from_isbn13, [lb.isbn13 for lb in lbs], chuncksize)

        # r = []
        # for x in it:
        #     if isinstance(x, AladinBook):
        #         r.append(x)
        # return r

def most_popular_category(albs):
    c = Counter(CATEGORIES[b.categoryId][1:] for b in albs)
    return c.most_common()
