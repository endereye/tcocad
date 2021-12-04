# TCOCAD

该项目是重庆大学计算机学院本科数字图像处理课程期末项目的两个子项目之一。
**TCOCAD** 是 **Traditional Classifier Of Cats And Dogs**，即 **传统猫狗分类器** 的简称。
顾名思义，该项目实现了一个传统的（即不基于深度学习的）、针对猫狗图像的分类器。

如果你只关心分类器的原理而不关心 GUI 的实现，你只需要关注 [core/core.py](https://github.com/endereye/tcocad/blob/main/core/core.py) 即可。

## 模型架构

该项目使用 SIFT 算法进行特征提取，基于 BOW 技术构建特征向量，并使用 SVM 作为分类器。
所有训练和测试用的图片均以灰度图的形式读取，并会被重新缩放为 $ S \times S $ 大小。

### 超参设置

- $ F $：SIFT 算法提取到的特征数量的最大值，默认为 256；
- $ S $：图像缩放之后的大小，默认为 256；
- $ K $：聚类的数量，亦为特征向量的维度，默认为 32。

在 [core/core.py](https://github.com/endereye/tcocad/blob/main/core/core.py) 的开头处可修改上述超参。
**但请注意：修改过后，之前训练的模型将无法再被使用。**
其余超参，均使用对应框架（OpenCV、sklearn）的默认值。

### SIFT 算法

SIFT 算法是一种在 1999 年由 David G.Lowe 提出的，基于尺度空间的图像局部特征提取算法。
该算法具有以下特点：

1. 对旋转、尺度缩放、亮度变化保持不变性；
2. 独特性：信息量丰富，适用于在海量特征数据中进行快速，准确的匹配；
3. 多量性：即使少数几个物体也可以产生大量的特征；
4. 可扩展性：可以很方便的与其他形式的特征向量进行联合；

该项目中，我们使用 OpenCV 实现的 SIFT 算法进行特征提取。

### BOW 模型

BOW 模型，即词袋模型，最早出现在自然语言处理领域。
该模型把文章看作单词的集合，通过建立词典并统计文章中每个单词的数量，实现文本内容分类。
该模型后被迁移至图像分类领域，又称为 Bag of Features 模型。

在 SIFT 算法提取到的特征中，有一些特征是极为相似的。
通过 KMeans 聚类算法， 我们可以找到这些相似特征的簇心，这些簇心即为 BOW 模型中的“单词”。
对于一张图像，我们将其的 SIFT 特征映射到这些“单词”上，并依此统计这张图像所包含的每种“单词”的数量，即这张图像的特征向量。

该模型得到的特征向量维数为 $ K $，远小于 SIFT 算法提取到的特征，可直接作为 SVM 的输入。

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
