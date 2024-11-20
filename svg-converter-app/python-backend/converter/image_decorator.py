import matplotlib

matplotlib.use("Agg")  # GUIバックエンドを使用しないように設定
import base64
import io

import matplotlib.pyplot as plt


# base64でグラフを変換する
def output_base64(func) -> str:
    def warapper(*args, **kwargs):
        buf = io.BytesIO()
        func(*args, *kwargs)

        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode("utf-8")

        return image_base64

    return warapper
