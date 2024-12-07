from setuptools import setup, find_packages


# requirements.txtを読み込む関数
def parse_requirements(filename):
    with open(filename, "r") as file:
        return file.read().splitlines()


setup(
    name="svg2csv",  # パッケージ名（pip listで表示される）
    version="2.0.0",  # バージョン
    description="MEA計測データを読み込み・解析するためのモジュール",  # 説明
    packages=find_packages(),  # 使うモジュール一覧を指定する
    install_requires=parse_requirements("requirements.txt"),
    license="MIT",  # ライセンス
)
