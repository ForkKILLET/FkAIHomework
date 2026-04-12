#set page(margin: 1cm, paper: "iso-b5")
#set text(font: "Sarasa Gothic SC", lang: "zh")
#show math.equation.where(block: true): el => [
  #block(width: 100%, inset: 0em, [
    #set align(center)
    #el
  ])
]

== 问题

#let Ras = math.op("Ras")
#let fitness = math.op("fitness")

已知 Rastrigin 函数

$ Ras(x) = 20 + x_1^2 + x_2^2 - 10 (cos 2 π x_1 + cos 2 π x_2). $

用 GA（遗传算法）求函数 $Ras$ 的极小值点.

理论解：$(0, 0)$.

精度：假设与例题相同，要求精度不大于 $0.01$.

== 步骤

1. 定义适应度函数

  因为这是一个最小化问题，我们可以定义适应度函数为

  $ fitness(x) = - Ras(x). $

2. 确定解的染色体编码

  使用实数编码：$(x_1, x_2)$.

3. 初始化种群

  在 $[-5.12, 5.12]$ 内按均匀分布随机生成.

4. 遗传算法循环

  - 计算适应度

  - 找出、更新最优解

  - 提取精英

  - 选择：锦标赛选择

  - 交叉：线性交叉

    $ x_"offspring" = α x_"parent"_1 + (1 - α) x_"parent"_2 $

  - 变异：高斯变异

    $ x' = x + N(0, σ^2) $

  - 放回精英