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
    pagenation_sauce = base_url + target_model + "/?pn="
    pagenation_list = []

    for i in range(1, n + 1):
        pagenation_i = str(i)
        pagenation_num = pagenation_sauce + pagenation_i
        pagenation_list.append(pagenation_num)
    return pagenation_list


def search_detail_path(target_model, pagenation_url_list) -> list:
    """
    詳細ページへのパスを取得する
    """
    detail_path_list = []
    for pagenation_url in pagenation_url_list:
        res = requests.get(pagenation_url)
        soup = BeautifulSoup(res.text, "html.parser")
        extract_href = [
            href_cid.get("href")
            for href_cid in soup.find_all("a")
            if href_cid.get("href") and "aspx?cid" in href_cid.get("href")
        ]
        for href_tag in extract_href:
            if f"/car/{target_model}/review/detail.aspx?cid=" in href_tag:
                detail_path_list.append(href_tag)
    unique_path_list = sorted(list(set(detail_path_list)), reverse=True)
    print(len(unique_path_list))
    return unique_path_list


def main():
    base_url = "https://minkara.carview.co.jp/car/"
    review_url = "https://minkara.carview.co.jp/car/toyota/crown_crossover/review/"
    n = 3

    target_model = split_review_model(base_url, review_url)
    pagenation_url_list = make_pagenation_url(review_url, target_model, n)
    print(pagenation_url_list)
    detail_path_list = search_detail_path(target_model, pagenation_url_list)


if __name__ == "__main__":
    main()
