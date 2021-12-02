# TCOCAD

该项目是重庆大学计算机学院本科数字图像处理课程期末项目的两个子项目之一。
**TCOCAD** 是 **Traditional Classifier Of Cats And Dogs**，即 **传统猫狗分类器** 的简称。
顾名思义，该项目实现了一个传统的（即不基于深度学习的）、针对猫狗图像的分类器。

如果你只关心分类器的原理而不关心 GUI 的实现，你只需要关注 [core/core.py](https://github.com/endereye/tcocad/blob/main/core/core.py) 即可。

## 模型架构

该项目使用 SIFT 算法进行特征提取，基于 BOW 技术构建特征向量，并使用 SVM 作为分类器。
所有训练和测试用的图片均以灰度图的形式读取，并会被缩放为 $ S \times S $ 大小。

### 训练流程

1. 训练图片使用 SIFT 算法提取不超过 $ F $ 个特征；
2. 对所有图片的特征进行 KMeans 聚类，划分出 $ K $ 个簇心；
3. 根据每张图片的特征，结合第 2 步得到的簇心，为每张图片构建一个 $ K $ 维特征向量（此特征向量不同于 SIFT 算法提取的特征）；
4. 以每张图片的特征向量作为输入，训练 SVM；
5. 保存模型时，只需要保存第 2 步得到的簇心以及第 4 步得到的 SVM。

### 预测流程

1. 预测图片使用 SIFT 算法提取不超过 $ F $ 个特征；
2. 根据这些特征，结合模型中保存的簇心，构建一个 $ K $ 维特征向量；
3. 以特征向量作为输入，通过模型中保存 SVM 计算得到分类结果。

### 超参设置

- $ F $：SIFT 算法提取到的特征数量的最大值，默认为 256；
- $ S $：图像缩放之后的大小，默认为 256；
- $ K $：聚类的数量，亦为特征向量的维度，默认为 32。

在 [core/core.py](https://github.com/endereye/tcocad/blob/main/core/core.py) 的开头处可修改上述超参。
**但请注意：修改过后，之前训练的模型将无法再被使用。**
其余超参，均使用对应框架（`OpenCV`、`sklearn`）的默认值。

### 相关资料：

 - [SIFT](https://zhuanlan.zhihu.com/p/261965433)
 - [KMeans](https://zhuanlan.zhihu.com/p/78798251)
 - [BOW](https://www.jianshu.com/p/7aceda6a0487)
 - [SVM](https://zhuanlan.zhihu.com/p/77750026)

## 数据来源、预处理及训练结果

所有训练和测试用的数据均来自 [Oxford-IIIT](https://www.robots.ox.ac.uk/~vgg/data/pets/) 数据集。
该数据集包含了超过 7000 张不同品种的猫狗照片，但该项目仅使用了其中的 3686 张照片的头部区域。
训练数据集与测试数据集按 4 比 1 的比例随机分隔，并保证训练数据集中猫狗照片的数量相等。
分隔时所使用的随机种子可能会对模型的性能造成细微影响。
具体预处理过程请参见 [data/preprocess.py](https://github.com/endereye/tcocad/blob/main/data/preprocess.py)。 

下表为模型在训练数据集上的准确率：

| 类别 | 图片数量 | 正确数量 | 准确率 |
|:---:|:---:|:---:|:---:|
| 猫 | 950 | 790 | 83% |
| 狗 | 950 | 822 | 86% |
| 合计 | 1900 | 1612 | 84% |

下表为模型在测试数据集上的准确率：

| 类别 | 图片数量 | 正确数量 | 准确率 |
|:---:|:---:|:---:|:---:|
| 猫 | 238 | 171 | 71% |
| 狗 | 1185 | 1548 | 76% |
| 合计 | 1356 | 1786 | 75% |

## 使用指南

下载并安装所需要的 Python 包即可：

```sh
git clone git@github.com:endereye/tcocad.git
pip install -r requirements.txt
python main.py
```

使用过程也可参见[介绍视频](https://raw.githubusercontent.com/endereye/tcocad/main/docs/mix.mp4)。

### 训练

1. 首先下载并解压原始数据集：

   ```sh
   cd data
   wget 'https://www.robots.ox.ac.uk/~vgg/data/pets/data/images.tar.gz'
   wget 'https://www.robots.ox.ac.uk/~vgg/data/pets/data/annotations.tar.gz'
   tar -zxvf images.tar.gz
   tar -zxvf annotations.tar.gz
   ```

2. 随后运行预处理脚本：

   ```sh
   python preprocess.py
   ```

3. 启动程序，选择 `[训练] > [训练模型]` 菜单选项，并在弹出的对话框中指定训练数据集：

   ![](https://raw.githubusercontent.com/endereye/tcocad/main/docs/train-3.png)

4. 等待训练完成：

   ![](https://raw.githubusercontent.com/endereye/tcocad/main/docs/train-4.png)

5. 训练完成后，选择模型文件的保存位置：

   ![](https://raw.githubusercontent.com/endereye/tcocad/main/docs/train-5.png)

### 预测

1. 启动程序，选择 `[训练] > [加载模型]` 菜单选项，并选择之前保存的模型文件；
   如果之前刚刚训练过模型，则可跳过这一步：

   ![](https://raw.githubusercontent.com/endereye/tcocad/main/docs/predict-1.png)

2. 此时窗口下方的进度条应当显示 `就绪`：

   ![](https://raw.githubusercontent.com/endereye/tcocad/main/docs/predict-2.png)

3. 选择 `[预测] > [打开图片]` 菜单选项，并选择一张图片；
   窗口将显示图片本身以及提取到的特征，并显示分类结果：

   ![](https://raw.githubusercontent.com/endereye/tcocad/main/docs/predict-3.png)

### 评估

1. 重复预测过程的第 1 步和第 2 步。

2. 选择 `[预测] > [评估模型]` 菜单选项，并在弹出的对话框中指定测试数据集：

   ![](https://raw.githubusercontent.com/endereye/tcocad/main/docs/measure-2.png)

3. 等待评估完成：

   ![](https://raw.githubusercontent.com/endereye/tcocad/main/docs/measure-3.png)

4. 评估完成后，将显示评估结果（准确率）：

   ![](https://raw.githubusercontent.com/endereye/tcocad/main/docs/measure-4.png)
