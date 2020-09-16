from pprint import pprint

import pytest
import scraping

HOW_MUCH = 500

@pytest.fixture(scope='module')
def library_high_school():
    res = scraping.library_high_school(HOW_MUCH)
    assert len(res) == HOW_MUCH
    return res

@pytest.fixture(scope='module')
def aladin_from_library(library_high_school):
    res = scraping.library_to_aladin(library_high_school)
    return res


def test_aladin():
    abook = scraping.aladin_from_isbn13("9788950981181")
    assert abook.title == "사람이 귀엽게 보이는 높이"

    assert scraping.CATEGORIES[51373][0] == "외국에세이"
    assert scraping.CATEGORIES[51373][1] == "에세이"
    assert scraping.CATEGORIES[51373][2] == "외국에세이"


# # @pytest.mark.skip(reason="많은 걸 뽑아낼 수 있는 확인하고 싶을 때만")
# def test_library_many():
#     bs = scraping.library_high_school(HOW_MUCH)
#     assert len(bs) == HOW_MUCH
#     assert isinstance(bs[0], scraping.LibraryBook)


def test_library_to_aladin(library_high_school, aladin_from_library):
    bs = library_high_school
    assert len(bs) > 0
    assert isinstance(bs[0], scraping.LibraryBook)

    lb_not_exist = scraping.LibraryBook(
        no=10,
        ranking="10",
        bookname="나미야 잡화점의 기적 :히가시노 게이고 장편소설 ",
        authors="지은이: 히가시노 게이고 ;옮긴이: 양윤옥",
        publisher="현대문학",
        publication_year="2012",
        isbn13="9788990809177",
        addition_symbol="03830",
        vol="",
        class_no="833.6",
        loan_count="11,323",
        bookImageURL="http://image.aladin.co.kr/product/15848/6/cover/k622533431_1.jpg",
    )  # isbn만 중요 나머지는 다 상관 없음..

    bs.append(lb_not_exist)

    albs = aladin_from_library
    assert len(albs) > 0
    assert isinstance(albs[0], scraping.AladinBook)

def test_most_popular(library_high_school, aladin_from_library):
    albs = aladin_from_library
    pprint( scraping.most_popular_category(albs))
    assert 0
