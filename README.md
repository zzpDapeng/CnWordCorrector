# CnWordCorrector
Specialized Chinese Word Document Corrector
# 天智杯文本纠错技术报告

### 一、纠错类型

1. 字词错误
2. 标点符号错误
3. 专用名词错误
4. 固定搭配错误（未实现）
5. 语法错误（未实现）
6. 上下文错误
7. 索引错误
   - 目录-标题索引错误
   - 附图索引错误

---

### 二、整体流程

文本纠错的整体流程如下：

1. Word文件预处理
2. 分类纠错
3. 根据纠错结果标记Word文档

---

### 三、技术细节

#### 1.Word预处理

##### 1. 环境

```shell
python-docx==0.8.10 
pypiwin32==223  # 只能在安装windows环境下安装(作用：将doc批量转docx，除此步骤之外不限定系统环境)
```

##### 2. 功能

doc转docx，读取word文档内容。

##### 3. 技术细节

1. 首先在windows环境下，使用python的win32com将可能存在doc文件转换为docx文件，因为docx库只能处理docx文件。
2. 使用python的docx库格式化解析word文档，根据比赛的要求划分目录、正文、标题、句子、附图等。将解析的结果存储到格式化json文件中，为各类纠错提供文本数据。
3. 目录，标题、正文、附图划分的主要依据是word字体和字号。

##### 4. 说明

1. 所有数据（doc、docx、jpg）均保存在在同一文件夹下

2. 先在windows环境下通过doc2docx.py文件内的doc2docx()函数，将所有doc文件批量转换成docx文件，再进行后续处理（后续处理可在其他环境下运行，不再局限于windows）

3. data.json文件说明：

   - json整体结构

     <img src="https://gitee.com/zzp_dapeng/PicBeg/raw/master/img/20200930155545.png" style="zoom: 67%;" />

   - sentences字段：包含文章中所有句子（无换行符、空行等）

     <img src="https://gitee.com/zzp_dapeng/PicBeg/raw/master/img/20200930155604.png" style="zoom:67%;" />

   - catalogue_titles字段:目录中的标题。（用于索引纠错）

     <img src="https://gitee.com/zzp_dapeng/PicBeg/raw/master/img/20200930155621.png" style="zoom:67%;" />

   - subtitles字段：标题

     <img src="https://gitee.com/zzp_dapeng/PicBeg/raw/master/img/20200930155717.png" style="zoom:67%;" />

   - paragraphs字段：正文段落

     <img src="https://gitee.com/zzp_dapeng/PicBeg/raw/master/img/20200930155749.png" style="zoom:67%;" />

   - figures字段：附图、附件

     <img src="https://gitee.com/zzp_dapeng/PicBeg/raw/master/img/20200930155848.png" style="zoom:67%;" />



---

#### 2.字词错误

**主要工具：原理**

pycorrector

**原理：**

字词错误主要是针对正文中的错字进行纠正，使用的是pycorrector，这是一个开源的中文纠错工具，比赛中使用的是基于深度模型的纠错方法，深度模型选择的是bert，因为bert的预训练任务MLM比较适合文本纠错，MLM任务是对句子中的文字进行mask，然后训练模型根据上下文信息预测mask位置的文字是什么。将其对应到文本纠错中，就是依次对句子中的每个字进行mask，通过bert进行预测该位置上的文字，比较预测结果与实际结果，两者出现不一致时，说明该位置需要进行纠正，根据模型预测结果与生成的候选文字集合对该位置文字进行纠正。



---

#### 3.标点符号错误

判断正文段落结尾是否有标点符号，若没有则添加句号。



---

#### 4.专用名词错误

##### 1. 错误检测

通过以下四种方法共同检测疑似错误的位置

**1.1 基于混淆词典**

- 混淆词典格式如下：

  ![](https://gitee.com/zzp_dapeng/PicBeg/raw/master/img/confusion.png)

- 正向最长匹配
  通过正向最长匹配，匹配同时出现在句子和混淆词典中的词语，添加到疑似错误列表

**1.2 基于分词**

- 混淆词典格式如下：

  ![](https://gitee.com/zzp_dapeng/PicBeg/raw/master/img/word_dict.png)

- 通过分词后检索当前词是否存在于通用词典word_dict中

- 未登录词加入疑似错误列表

**1.3 基于word gram**

基于 **词** 的错误检测

- 分词后基于一元，二元，三元语法并通过语言模型给每个token打分，再通过平均绝对离差(mean absolute deviation)将分数大于规定阈值的疑似错字并加入疑似错误列表

**1.4 基于char gram**

基于 **字** 的错误检测

- 以字为单位，基于一元，二元，三元和四元语法并通过语言模型给每个token打分，再通过平均绝对离差(mean absolute deviation)将分数大于规定阈值的疑似错字并加入疑似错误列表

##### 2. 错误纠正

获取所有疑似错误后，进行错误校准（即将错误类型同为char且位置相邻的错误拼接起来）

**2.1 混淆词典检测出的错误直接得到正确答案**

1.1中检索出的错误（变体），将直接由右侧正确答案（本体原理）替换

**2.2 获取所有候选词**

- 通过编辑距离

  ```
  def edits1(self, word):
      """All edits that are one edit away from `word`."""
      splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
      transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
      replaces = [L + c + R[1:] for L, R in splits if R for c in self.char_set]
      return set(transposes + replaces)
  ```

- 通过近似拼音

  ```
  def _candidates_by_pinyin(self, word):
      l = []
      r = list(self.pinyin2word.get(','.join(lazy_pinyin(word)), {word:''}).keys())
      for i, w in enumerate(word):
          before = word[:i]
          after = word[i+1:]
          a = list(self.same_pinyin_dict.get(w, w))
          l += [before+x+after for x in a]
  
      return set(l + r)
  ```

- 通过近似字形

  ```
  def _candidates_by_stroke(self, word):
      l = []
      for i, w in enumerate(word):
          before = word[:i]
          after = word[i + 1:]
          a = list(self.same_stroke_dict.get(w, w))
          l += [before + x + after for x in a]
  
      return set(l)
  ```

**2.3 通过语言模型纠正字词错误**

遍历所有候选词，组成新句子，从所有新句子中通过给定阈值选出前k个候选词（利用语言模型打分）

- 若原词包含在k个里边，则选原词
- 若原词不包含在k个里边，则选得分最高的

**2.4 筛选出可能的专有名词错误**

- 遍历所有字词错误，通过正向最长匹配（给定窗口大小），选出在word_dict中出现过的名词

  - 匹配成功，则将此处视为专有名词错误
  - 匹配失败，则不将此处记为错误

- 错误格式修正，去除错误与答案的共同部分
  有时因为分词的原因，标记的错误有多余部分，如下图中的**及**，修正此类错误

    ```
    ('京津冀及周边、长三角和西北区域大部地区以良至轻度污染为主', [['既及', '冀及', 2, 4]])
    ```

##### 3. 模型效果

正向最长匹配的窗口大小设置为5，所以虽然将 **凡** 改成了 **范** ，但并没有在word_dict里成功匹配到**首都师范大学**，所以结果为[]，模型效果取决于词典好坏、分词效果以及语言模型

![](https://gitee.com/zzp_dapeng/PicBeg/raw/master/img/young_corrector_run.png)



---

#### 5.上下文错误

**错误描述：**

在用一个段落中，内容采用枚举说明时，会采用总分结构，例如上文：4个方面，下文：第一个、第二个、第三个、第四个，如果上文总数对应不上下文的序号，则会发生错误，要求进行发现错误并改正错误，并返回一定格式的数原理据报。

**所用的库**

1. re   使用re库正则表达式建立刷选规则
2. json  使用json库来编码和解码 JSON 对象 

**纠错规则：**

1. 使用json库调用load()方法去加载待纠错的文件，从而获取内容内容。
2. 依次遍历文件内容并记录清楚错误发生的内容在整个文件中的具体位置，例如在第几大标题、第几段落、第几句话以及第几个字。
3. 通过re库调用compile()方法来找出所有的段落包含的中文、阿拉伯数字，以及包括修饰量词，如“四个方面、三方面，一是、二个”等，每个段落单独使用一个列表单独保存这些数字量词。
4. 然后以上文的数字量词为基准，分别在其后下文的数字量词一一比对，如果发现下文最大的数字量词不等于上文的数字量词，则发生了错误，记录出上文发生错误的位置。
5. 将发生错误的上文对应位置的数字替换为下文中最大数字，然后将记录到的错误发生的位置信息按照规定的格式做成数据报返回即可。



---

#### 6.目录-标题索引错误

##### 1. 环境

```
python==3.6.0
# 核心工具difflib，python自带库，不需要安装 
```

##### 2. 功能

对比目录和标题，找出其中缺字、多字、错字的情况

##### 3. 技术细节

1. 获取json中对应的目录和标题对
2. 使用difflib库对比两个句子
3. 根据对比结果解析错误发生的位置和错误类型



---

#### 7.附图索引错误

**主要工具**：

PaddleOCR、difflib

**原理：**

这种错误主要是文本与图片中标题文字不对应产生的，修正只需要对照图片中文本进行修改即可。首先使用paddleocr识别出图片中的标题，然后借助difflib这个库提供的SequenceMatcher方法，对比图片中标题与正文中标题差异，根据结果返回修改内容。



---

#### 8.标记word文档

##### 1. 环境

```shell
python-docx==0.8.10 
```

##### 2. 功能

根据识别出的错误，在原word文档的错误位置标黄

##### 3. 技术细节

实现过程中依次设计了三种方案

- 方案一、根据json数据从0开始生成word文件
  - 问题：即便在代码中指定了文本样式，最终生成的样式与原始文件依然不统一
- 方案二、根据原始文档，判断paragraph和run（docx最小处理单位）错误情况，选择是否标记。
  - 问题：只能标记到run，而run不能具体到句子和字，因此无法满足标记要求
  - 样式也存在一定问题
- 方案三、复制原始文档，在原文档生成的对象上进行修改。
  - 可以完美解决样式的问题，与原文件样式保持一致
  - 可以精确标注错误位置

最终采用了方案三。

因为根据错误信息无法得知该错误是否属于**缺字错误**，因此不能依据最终提交的错误信息文件标记word，约定了新的错误信息文件格式来标记word