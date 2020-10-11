from pprint import pprint

import pytest
import xmltodict

import scraping

HOW_MUCH = 30


@pytest.fixture(scope="module")
def library_high_school():
    res = scraping.library_high_school(HOW_MUCH)
    return res


@pytest.fixture(scope="module")
def aladin_from_library(library_high_school):
    res = scraping.library_to_aladin(library_high_school)
    return res


# @pytest.mark.skip
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


# @pytest.mark.skip
def test_a_library_high_school():
    apage = scraping.a_library_high_school(1)
    assert len(apage) == scraping.PAGE_SIZE
    assert isinstance(apage[0], scraping.LibraryBook)


# @pytest.mark.skip
def test_library_high_school(library_high_school):
    assert len(library_high_school) == HOW_MUCH


# @pytest.mark.skip
def test_aladin_from_library(aladin_from_library):
    assert len(aladin_from_library) > 0


# @pytest.mark.skip
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

    albs = scraping.library_to_aladin(bs)
    assert len(albs) > 0
    assert isinstance(albs[0], scraping.AladinBook)


# @pytest.mark.skip
def test_most_popular(library_high_school, aladin_from_library):
    albs = aladin_from_library
    x = scraping.most_popular_category(albs)
    assert isinstance(x, list)
    assert isinstance(x[0], tuple)
    assert len(x[0]) == 2
    # assert 0
    # 그냥 -rA 조건을 붙여주면 깔끔하게 정리된 출력을 볼 수 있다. 실패하지 않더라도.


def test_a_albs_list():
    l = scraping.a_albs_list(51123, "ItemNewSpecial", 1)
    assert isinstance(l[0], scraping.AladinBook)
    pprint(l[0])


def test_new_alb_from_xml():
    xml = """
<item itemId="5912511">
			    <title>덕혜옹주 - 조선의 마지막 황녀</title>
				<link>http://www.aladin.co.kr/shop/wproduct.aspx?ItemId=5912511&amp;copyPaper=1&amp;ttbkey=ttbjoshua1b28232354001&amp;start=api</link>
				<author>권비영 지음</author>
				<pubDate>Sun, 13 Dec 2009 15:00:00 GMT</pubDate> 
				<description>&lt;img src='https://image.aladin.co.kr/product/591/25/coveroff/8963700348_3.jpg'/&gt; 덕혜옹주 - 권비영 지음 &lt;br/&gt; 가장 고귀한 신분으로 태어났지만 가장 외롭게 생을 마감했던 덕혜옹주에 관한 소설이다. 작가는 덕혜옹주뿐 아니라 망국의 시대를 견뎌야 했던 모든 이들 ― 황제와 황족들, 청년들, 여자들과 아이들 ― 의 울분과 고통을 생생하게 되살리려고 노력했다.</description>
				<creator>aladin</creator> 
				<isbn>8963700348</isbn>
				<isbn13>9788963700342</isbn13>
				<priceSales>10620</priceSales>
				<priceStandard>11800</priceStandard>
				<stockStatus>구판절판</stockStatus>
				<mileage>48</mileage>
				<cover>https://image.aladin.co.kr/product/591/25/coversum/8963700348_3.jpg</cover>
				<categoryId>51123</categoryId>
				<categoryName>국내도서&gt;소설/시/희곡&gt;역사소설&gt;한국 역사소설</categoryName>
				<publisher>다산책방</publisher>
				<customerReviewRank>9</customerReviewRank>
                
				    <bookinfo>
				        <subTitle>조선의 마지막 황녀</subTitle>
		                <originalTitle></originalTitle>
				        <itemPage>416</itemPage>		            
		                <toc><![CDATA[<p>프롤로그_ 두 여인 <BR>
<BR>
<B>1부 그곳에 이름 없는 황녀가 살고 있었다</B><BR>
유령의 시간 ｜겨울이 지나면 봄이 오는가｜괴이한 소문｜비밀을 함께 나눈 이｜폭풍이 몰려오고 있다｜심연｜떠도는 자들｜인연｜그리운 사람들｜이름의 대가<BR>
<BR>
<B>2부 한겨울에 피는 꽃들</B><BR>
조선 유학생｜떨어지는 꽃잎처럼｜또 다른 죽음｜그림자 사나이｜누구도 원치 않았지만｜화선지 속에 감춘 것｜그날의 신부는<BR>
<BR>
<B>3부 말하라, 이 여자는 누구인가</B> <BR>
불행한 만남｜해빙｜두려운 날들｜사라지는 자와 태어나는 자｜정혜 혹은 마사에｜악몽｜살아야 하는 이유｜흔들리는 시간들｜곁에 아무도 없다｜<BR>
<BR>
<B>4부 아주 오랜 시간이 흐른 뒤에야</B> <BR>
요코와 사끼코｜꼭 한 번은 마주쳐야 했던｜탈출할 수 있을까｜해향에 얽힌 마음｜마지막 시도｜<BR>
<BR>
에필로그_ 모두의 기억에서 사라졌다 해도 나는 조선의 황녀였다.</p>]]></toc>
		                <letslookimg>https://image.aladin.co.kr/product/591/25/letslook/8963700348_fs.jpg</letslookimg>
                                <letslookimg>https://image.aladin.co.kr/product/591/25/letslook/8963700348_bs.jpg</letslookimg>
                                <letslookimg>https://image.aladin.co.kr/product/591/25/letslook/8963700348_t1s.jpg</letslookimg>
                                
                        <authors><author authorType="author" authorid="227245" desc="지은이">권비영</author></authors>
                        <ebookList>
                        
                        </ebookList>
				    </bookinfo>
				    				
			</item>
    """

    x = xmltodict.parse(xml)
    alb = scraping.new_alb_from_xml(x["item"])
    assert isinstance(alb, scraping.AladinBook)
    assert alb.isbn13 == 9788963700342


def test_albs_list():
    albs = scraping.albs_list(51123, "ItemNewSpecial")
    assert isinstance(albs[0], scraping.AladinBook)
    assert albs[0].isbn13 is not None
    assert len(albs) == scraping.total_albs_list(51123, "ItemNewSpecial")


def test_total_albs_list():
    # r = scraping.total_albs_list(51123, "ItemNewSpecial")
    r = scraping.total_albs_list(50930, "ItemNewSpecial")
    # r = scraping.total_albs_list(1, "ItemNewSpecial")
    pprint(r)
    assert isinstance(r, int)
    assert r > 0
    # assert r2 > 0
