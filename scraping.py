import requests
from bs4 import BeautifulSoup


def split_review_model(base_url, review_url: str) -> str:
    """
    urlから/maker/model/のパスを取り出す
    """
    behind = review_url.split(base_url)
    behind_split = behind[1].split("/review/")
    target_model = behind_split[0]
    return target_model


def make_pagenation_url(base_url: str, target_model: str, n: int) -> list:
    """
    ページネーションのurlを作成する
    """
    pagenation_sauce = base_url + target_model + "/review/?pn="
    # https://minkara.carview.co.jp/car/toyota/crown_crossover/review/?pn=2
    pagenation_list = []

    for i in range(1, n + 1):
        pagenation_i = str(i)
        pagenation_num = pagenation_sauce + pagenation_i
        pagenation_list.append(pagenation_num)
    return pagenation_list


def search_detail_path(target_model, pagenation_url_list) -> list:
    """
    詳細ページへのID情報を含むパスを取得する
    """
    for pagenation_url in pagenation_url_list:
        res = requests.get(pagenation_url)
        soup = BeautifulSoup(res.text, "html.parser")
        extract_href = [
            href_cid.get("href")
            for href_cid in soup.find_all("a")
            if href_cid.get("href") and "aspx?cid" in href_cid.get("href")
        ]
        target_model_path_list = [
            href_tag
            for href_tag in extract_href
            if f"{target_model}/review/detail.aspx?cid=" in href_tag
        ]
        detail_path_list = [
            target_model_path.split("/car/")[1]
            for target_model_path in target_model_path_list
        ]
    unique_path_list = sorted(list(set(detail_path_list)), reverse=True)
    return unique_path_list


def make_full_detail_url(base_url, detail_path_list):
    """
    ベースURLと詳細ページへのIDパスを合わせて、各詳細ページへのフルURLを作成
    """
    detail_url_list = [base_url + detail_path for detail_path in detail_path_list]
    return detail_url_list


def scrape_review_titles(detail_url: str) -> list:
    """
    詳細ページから、レビューのタイトルを取得する
    """
    # for detail_num in detail_url_list:
    res = requests.get(detail_url)
    soup = BeautifulSoup(res.text, "html.parser")
    review_titles = soup.find_all("dt", class_="kr_subttl review-data__title")
    review_titles_list = [review_title.text.strip() for review_title in review_titles]
    return review_titles_list


def get_titles():
    """
    指定した順序でキーのリストを返す
    """
    return [
        "満足している点",
        "不満な点",
        "総評",
        "デザイン",
        "走行性能",
        "乗り心地",
        "積載性",
        "燃費",
        "価格",
        "故障経験",
    ]


def scrape_review_contents(detail_url: str) -> list:
    """
    詳細ページから、レビューの内容を取得する
    """
    res = requests.get(detail_url)
    soup = BeautifulSoup(res.text, "html.parser")
    review_contents = soup.find_all("dd", class_="review-data__text")
    review_contents_list = [
        review_content.text.strip() for review_content in review_contents
    ]
    return review_contents_list


def match_title_and_content(
    review_titles_list: list, review_contents_list: list
) -> dict:
    """
    タイトルと内容を合わせて辞書に
    """
    review_dict = {}
    for i in range(len(review_titles_list)):
        review_dict[review_titles_list[i]] = review_contents_list[i]
    return review_dict


def collect_all_titles(review_titles_list):
    return sorted(list(set(review_titles_list)))


def scrap_all_reviews(detail_url_list: list) -> list:
    all_reviews_list = []
    for detail_url in detail_url_list:
        review_titles_list = scrape_review_titles(detail_url)
        review_contents_list = scrape_review_contents(detail_url)
        all_reviews = match_title_and_content(review_titles_list, review_contents_list)
        all_reviews_list.append(all_reviews)
    collect_all_titles(review_titles_list)
    return all_reviews_list


def create_reviews_dict(all_reviews_list):
    """
    タイトルをキーとして、コメントをバリューに辞書
    """
    total_reviews = []
    key_titles = get_titles()
    for review in all_reviews_list:
        reviews_dict = {}
        for key in key_titles:
            # キーが存在しない場合は空文字列を設定
            reviews_dict[key] = review.get(key, "")
        total_reviews.append(reviews_dict)
    return total_reviews


def main():
    base_url = "https://minkara.carview.co.jp/car/"
    review_url = "https://minkara.carview.co.jp/car/toyota/crown_crossover/review/"
    n = 1
    target_model = split_review_model(base_url, review_url)
    pagenation_url_list = make_pagenation_url(base_url, target_model, n)
    detail_path_list = search_detail_path(target_model, pagenation_url_list)
    detail_url_list = make_full_detail_url(base_url, detail_path_list)
    all_reviews_list = scrap_all_reviews(detail_url_list)
    total = create_reviews_dict(all_reviews_list)
    print(total[0])


if __name__ == "__main__":
    main()
