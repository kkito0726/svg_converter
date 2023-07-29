from setuptools import setup, find_packages


def _requires_from_file(filename):
    return open(filename).read().splitlines()


setup(
    name="svg2csv",  # パッケージ名（pip listで表示される）
    version="1.1.1",  # バージョン
    description="MEA計測データを読み込み・解析するためのモジュール",  # 説明
    packages=find_packages(),  # 使うモジュール一覧を指定する
    # install_requires=_requires_from_file("requirements.txt"),
    license="MIT",  # ライセンス
)
