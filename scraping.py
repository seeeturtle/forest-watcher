import functools
import json
import operator
import os
from collections import Counter, namedtuple
from multiprocessing import Pool, cpu_count
from pprint import pprint

import requests
import xlrd
import xmltodict
from tqdm import tqdm

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
    "salesPoint",
    "first_category",
    "second_category",
]

AladinBook = namedtuple(
    "AladinBook",
    _alb_fields,
)


def new_alb(**kwargs):
    base = {f: None for f in _alb_fields}
    base.update(kwargs)

    c = CATEGORIES[base["categoryId"]]
    base["first_category"] = c[1]
    base["second_category"] = c[2]

    return AladinBook(**base)


def new_alb_from_xml(item):
    item["itemId"] = item.pop("@itemId")
    removed_fields = set(item.keys()) - set(_alb_fields)
    for f in removed_fields:
        del item[f]
    for k, v in item.items():
        if isinstance(v, str) and v.isdigit():
            item[k] = int(v)

    c = CATEGORIES[item["categoryId"]]
    item["first_category"] = c[1]
    item["second_category"] = c[2]

    return new_alb(**item)


# ['version', 'title', 'link', 'pubDate', 'imageUrl', 'totalResults', 'startIndex', 'itemsPerPage', 'query', 'searchCategoryId', 'searchCategoryName', 'item']


def aladin_from_isbn13(isbn13):
    # 만약에 문자열중에서 isdigit을 만족하는 것이 있다면 int type 으로 변환시킨다.
    params = {
        "TTBKey": os.environ.get("ALADIN_API_KEY"),
        "ItemId": isbn13,
        "ItemIdType": "ISBN13",
        "Output": "XML",
    }

    r = requests.get("http://www.aladin.co.kr/ttb/api/ItemLookUp.aspx", params=params)

    # try:
    #     print("strange:")
    #     print(r.text.replace(";", "")[1326])
    # except:
    #     pass

    try:
        # j = json.loads(r.text.replace(";", "").replace(r"\'", "'"), strict=False)
        x = xmltodict.parse(r.text)
        item = x["object"]["item"]
        item = new_alb_from_xml(item)
    except:
        if "error" in x:
            print(f"\nisbn13: {isbn13}\nerror:\n{x}\n")
        else:
            with open("personal/error-xml.xml", "w") as f:
                f.write(r.text)
            raise

    try:
        return item
    except:
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
# print(len(CATEGORIES))


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
        "authKey": os.environ.get("LIBRARY_API_KEY"),
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
    if n <= PAGE_SIZE:
        return a_library_high_school(1)[:n]  # 한페이지만 가져올 거면 그냥 풀 만드는 것보다 직접하는 게 더 빠른듯.
    else:
        whole_requests = int(n / PAGE_SIZE) + (n % PAGE_SIZE > 0)  # 올림
        print(whole_requests)
        with Pool(cpu_count()) as p:
            res = p.imap(a_library_high_school, tqdm(range(1, whole_requests + 1)))
            res = functools.reduce(operator.concat, res)[:n]
            return res


# def library_high_school(n):
#     # 가장 인기많은 순서대로 n개를 가져온다.
#     params = {
#         "authKey": "API KEY",
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
    # 실제로 받는 건 원래 있는 것보다 더 적을 수 도 있다.
    # TODO
    return [
        x
        for x in tqdm(map(aladin_from_isbn13, [lb.isbn13 for lb in lbs]))
        if isinstance(x, AladinBook)
    ]


# 동시성 사용 버전의 알라딘
# def library_to_aladin(lbs):
#     with Pool(cpu_count()) as p:
#         chuncksize = int(len(lbs)/cpu_count() + 0.5) # 반올림
#         it = p.imap(aladin_from_isbn13, [lb.isbn13 for lb in lbs], chuncksize)

# r = []
# for x in it:
#     if isinstance(x, AladinBook):
#         r.append(x)
# return r


def most_popular_category(albs):
    x = []
    for b in albs:
        try:
            x.append(
                CATEGORIES[b.categoryId][1:] + (b.categoryId,)
            )  # [C1NAME, C2NAME, CID]
        except KeyError:
            print(f"error aladin book:\n{b}\nerror category:{b.categoryId}\n")
            # pass

    # pprint(x)

    c = Counter(x)
    return c.most_common()


LIST_SIZE = 50  # 리스트 요청 시 페이지당 아이ㅣ템의 개수

# QUERY TYPES : ["ItemNewAll", "ItemNewSpecial"]


def albs_list(category_id, qtype):
    # qtype은 알라딘 API 메뉴얼 참고
    # 정확히 몇개를 돌려줄지는 모름
    n = total_albs_list(category_id, qtype)
    if n <= LIST_SIZE:
        return a_albs_list(category_id, qtype, 1)
    whole_requests = int(n / LIST_SIZE) + (n % LIST_SIZE > 0)  # 올림
    with Pool(cpu_count()) as p:
        res = tqdm(
            p.imap(a_albs_list, range(1, whole_requests + 1)), total=len(whole_requests)
        )
        res = functools.reduce(operator.concat, res)

    return res


def total_albs_list(category_id, qtype):
    params = {
        "TTBKey": os.environ.get("ALADIN_API_KEY"),
        "QueryType": qtype,
        "Version": "20131101",
        "SearchTarget": "Book",
        "Start": 1,
        "MaxResults": LIST_SIZE,
        "CategoryId": category_id,
        "Output": "XML",
    }
    res = requests.get("http://www.aladin.co.kr/ttb/api/ItemList.aspx", params=params)

    try:
        x = xmltodict.parse(res.text)
        total = int(x["object"]["totalResults"])
    except:
        raise

    with open("personal/error-xml.xml", "w") as f:
        f.write(res.text)
    return total


def a_albs_list(category_id, qtype, page):
    params = {
        "TTBKey": os.environ.get("ALADIN_API_KEY"),
        "QueryType": qtype,
        "Version": "20131101",
        "SearchTarget": "Book",
        "Start": page,
        "MaxResults": LIST_SIZE,
        "CategoryId": category_id,
        "Output": "XML",
        "Cover": "Big",  # 너비 200px 크기
    }
    res = requests.get("http://www.aladin.co.kr/ttb/api/ItemList.aspx", params=params)

    try:
        x = xmltodict.parse(res.text)
        items = x["object"]["item"]
    except:
        return []

    r = []
    for i in items:
        try:
            r.append(new_alb_from_xml(i))
        except:
            raise
            pass

    return r


def main():
    from pymongo import MongoClient

    client = MongoClient(os.environ.get("MONGO_CLIENT"))

    db = client.forest_watcher_dev

    # lbs = library_high_school(500)
    # albs = library_to_aladin(lbs)
    # cs = most_popular_category(albs)

    #     categories = db.categories
    #     categories.insert_many(
    #         {"first_category": x[0], "second_category": x[1], "category_id": x[2]}
    #         for x in cs
    #     )

    # items = db.items
    # items.insert_many()
