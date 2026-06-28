# LUsolve

## `ans = A.LUsolve(b)` 完整讲解

### 一、基础前提：方程形式

我们要解线性方程组：
$$A\boldsymbol x = \boldsymbol b$$

- $A$：$n\times n$ 方阵（必须可逆，否则 LU 分解失败）
- $\boldsymbol b$：右端常数向量/矩阵
- $\boldsymbol x$：待求解，也就是代码里的 `ans`

`A.LUsolve(b)` 是面向对象写法，底层逻辑 = **先 LU 分解 A，再分两步三角回代求 x**

### 二、第一步：LU 分解 $A=LU$

高斯消元把 $A$ 拆成两个三角矩阵：

1. $L$：**单位下三角矩阵**，对角线全 1，记录消元的乘数；

$$
L=
\begin{bmatrix}
1 & 0 & 0 \\
l_{21} & 1 & 0 \\
l_{31} & l_{32} & 1
\end{bmatrix}
$$

2. $U$：**上三角矩阵**，高斯消元后的阶梯矩阵

$$
U=
\begin{bmatrix}
u_{11} & u_{12} & u_{13} \\
0 & u_{22} & u_{23} \\
0 & 0 & u_{33}
\end{bmatrix}
$$

于是原方程改写：
$$LU\boldsymbol x = \boldsymbol b$$

### 三、LUsolve 分两步求解（核心逻辑）

令中间变量 $\boldsymbol y = U\boldsymbol x$，方程拆成两个简单三角方程组：

#### 1）前向代换：解 $L\boldsymbol y = \boldsymbol b$

$L$ 是下三角，从上到下逐行直接算出 $\boldsymbol y$，计算量只有 $O(n^2)$
示例 3 阶：

$$
\begin{cases}
y_1 = b_1 \\
l_{21}y_1 + y_2 = b_2 \\
l_{31}y_1 + l_{32}y_2 + y_3 = b_3
\end{cases}
$$

#### 2）回代（反向代换）：解 $U\boldsymbol x = \boldsymbol y$

$U$ 是上三角，从最后一行往回倒推求出最终解 $\boldsymbol x$：

$$
\begin{cases}
u_{11}x_1 + u_{12}x_2 + u_{13}x_3 = y_1 \\
u_{22}x_2 + u_{23}x_3 = y_2 \\
u_{33}x_3 = y_3
\end{cases}
$$

先求 $x_3$，再代入求 $x_2$，最后求 $x_1$。

### 四、`A.LUsolve(b)` 执行流程（代码对应）

```python
ans = A.LUsolve(b)
```

内部自动执行完整流水线，用户不用手动拆分 LU：

1. 对矩阵 $A$ 做 LU 分解，缓存 $L、U$；
2. 用 $L、b$ 前向求解中间向量 $\boldsymbol y$；
3. 用 $U、\boldsymbol y$ 回代求出解 $\boldsymbol x$；
4. 将 $\boldsymbol x$ 作为返回值赋值给 `ans`。

### 五、核心优势

1. **多组右端向量极高效**
   若要解 $Ax=b_1,\ Ax=b_2,\dots$：
   - 普通直接消元：每组 b 都要完整做 $O(n^3)$ 消元；
   - LUsolve：**仅第一次分解 A 消耗$O(n^3)$**，后面所有 b 只需要两次$O(n^2)$三角代换，大幅提速。
2. 三角矩阵求解计算量远小于完整高斯消元。

### 六、关键限制与补充（PLU）

1. LU 分解**不允许主元为 0**：消元时如果对角线元素是 0，必须换行；
2. 实际库中实现的是**PLU 分解** $PA=LU$（$P$置换矩阵记录行交换），`LUsolve`内部会自动处理置换；
3. 仅支持**可逆方阵**；长方形矩阵（最小二乘）不能用 LUsolve，改用 QR/SVD。

### 七、简单数值例子

方程组：

$$
\begin{cases}
2x_1 + x_2 = 5 \\
x_1 + 4x_2 = 9
\end{cases},\quad
A=\begin{bmatrix}2&1\\1&4\end{bmatrix},\ \boldsymbol b=\begin{bmatrix}5\\9\end{bmatrix}
$$

1. LU 分解：

$$
L=\begin{bmatrix}1&0\\0.5&1\end{bmatrix},\quad
U=\begin{bmatrix}2&1\\0&3.5\end{bmatrix}
$$

2. 解 $L\boldsymbol y=\boldsymbol b$：

$$
\begin{cases}
y_1=5 \\
0.5y_1+y_2=9 \Rightarrow y_2=6.5
\end{cases}
$$

3. 解 $U\boldsymbol x=\boldsymbol y$：

$$
\begin{cases}
2x_1+x_2=5 \\
3.5x_2=6.5 \Rightarrow x_2=\dfrac{13}{7},\ x_1=\dfrac{11}{7}
\end{cases}
$$

`ans = A.LUsolve(b)` 会直接输出 $\boldsymbol x=[\tfrac{11}{7},\tfrac{13}{7}]$。

### 八、一句话总结

`A.LUsolve(b)` = 自动对系数矩阵 A 做 LU 三角分解，拆成两次低成本三角方程组求解，快速得到 $Ax=b$ 的解 `ans`，是批量求解线性方程组的标准高效算法。

## LU 分解 + LUsolve 完整讲解

### 一、先铺垫：什么是 LU 分解

对方阵 \(A\)，做高斯消元，不用行交换时可以拆成：
\[
A = LU
\]

- \(L\)：**下三角矩阵**，对角线全为 1，存消元时的消去乘数；
- \(U\)：**上三角矩阵**，就是高斯消元后得到的阶梯形矩阵。

例：
\[
A=
\begin{bmatrix}
2 & 1 \\
1 & 4
\end{bmatrix},\quad
L=
\begin{bmatrix}
1 & 0 \\
0.5 & 1
\end{bmatrix},\quad
U=
\begin{bmatrix}
2 & 1 \\
0 & 3.5
\end{bmatrix}
\]
验算：\(LU=A\)。

### 二、为什么要有 LUsolve？目标方程 \(Ax=b\)

普通解法：

1. 直接高斯消元 \(A\boldsymbol x=\boldsymbol b\)，每次换右侧向量 \(\boldsymbol b\) 都要完整消元，重复计算、慢。

LU 分解思路（分两步三角回代）：
\[
A\boldsymbol x = \boldsymbol b \Rightarrow LU\boldsymbol x = \boldsymbol b
\]
令中间变量 \(\boldsymbol y = U\boldsymbol x\)，拆成两个简单三角方程组：

1. **前向代入**：\(L\boldsymbol y = \boldsymbol b\)（下三角，从上往下快速解 \(\boldsymbol y\)）
2. **回代**：\(U\boldsymbol x = \boldsymbol y\)（上三角，从下往上快速解 \(\boldsymbol x\)）

### 三、LUsolve 函数的含义

`LUsolve(A, b)` / `linalg.lu_solve` / R 的 `solve(A)` 底层 LU 逻辑：

1. 先对系数矩阵 \(A\) 一次性算出 \(L,U\)；
2. 执行前向代入解 \(L\boldsymbol y=\boldsymbol b\)；
3. 执行回代解 \(U\boldsymbol x=\boldsymbol y\)；
4. 返回最终解 \(\boldsymbol x\)。

#### 巨大优势（工程/数值计算核心）

如果有多组右侧向量 \(b_1,b_2,\dots,b_k\)：

- 传统方法：每组 \(b\) 完整消元一次，复杂度 \(O(kn^3)\)；
- LU 方法：只分解一次 \(A\)（\(O(n^3)\)），每组 \(b\) 仅两次三角回代（\(O(n^2)\)），大规模计算速度碾压。

### 四、分语言实操示例

#### 1. Python NumPy

```python
import numpy as np
from scipy.linalg import lu_factor, lu_solve

A = np.array([[2, 1], [1, 4]])
b = np.array([5, 9])

## 1. 先 LU 分解，缓存分解信息
lu_fac = lu_factor(A)
## 2. LUsolve：代入 b 求解
x = lu_solve(lu_fac, b)
print(x) ## [1, 3]
```

#### 2. R

R 的 `solve(A,b)` 底层默认使用 LU 分解求解线性方程组，等价 LUsolve：

```r
A <- matrix(c(2,1,1,4), nrow=2)
b <- c(5,9)
x <- solve(A, b)
print(x)
```

### 五、补充关键限制

1. LU 分解**不支持行交换**：如果消元需要换行（主元为 0），要改用 PLU 分解（带置换矩阵 \(P\)：\(PA=LU\)），对应 `lu_factor` 会输出置换索引；
2. 只对方阵有效；非方阵最小二乘用 QR/SVD，不用 LU；
3. 数值稳定性：主元很小会放大浮点误差，工程上常搭配**选主元 PLU**。

### 六、极简总结

`LUsolve` = 先把系数矩阵拆成上下三角 \(L,U\)，再通过两次低成本三角回代快速求解 \(Ax=b\)，是多右侧向量场景下最高效的线性方程组解法。
