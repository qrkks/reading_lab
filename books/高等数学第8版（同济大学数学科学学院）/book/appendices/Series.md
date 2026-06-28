# SymPy `series()` 函数完整详解（泰勒展开专用）

## 一、基础定义与语法

`series()` 是 SymPy 专门生成**带佩亚诺余项的泰勒公式**的方法，作用：把一元函数在指定点展开为有限阶泰勒多项式，末尾附带大 O 余项 $\mathcal{O}(\cdot)$。

### 标准语法

```python
expr.series(variable, x0=展开中心点, n=展开最高阶数)
```

- `expr`：要展开的符号函数（如 `sp.exp(x)`、`sp.sin(x)`）
- `variable`：展开的自变量（必须单独指定，二元函数只能先对一个变量展开）
- `x0`：泰勒展开中心点，默认 `0`（麦克劳林展开）
- `n`：**截断阶数**，代表展开到 $(\text{var}-x_0)^{n-1}$ 项，余项是 $\mathcal{O}((\text{var}-x_0)^n)$

### 最简示例

```python
import sympy as sp
x = sp.Symbol("x")
sp.exp(x).series(x, 0, 4)
```

输出：
$$1 + x + \frac{x^2}{2} + \mathcal{O}\left(x^4\right)$$
参数 `n=4` → 最高写到 $x^3$，余项是 $x^4$ 阶无穷小。

## 二、核心组成：多项式 + 余项 $\mathcal{O}(\dots)$

### 1. 多项式部分

所有低于 $n$ 次的幂次项，就是我们说的**泰勒展开多项式**。

### 2. $\mathcal{O}(\dots)$ 大 O 余项（对应高数佩亚诺余项 $o(x^n)$）

- 含义：所有高于等于 $n$ 次的高阶项全部打包简写；
- 作用：标记截断后的误差量级；
- 去除余项方法：`.removeO()`

```python
# 去掉余项，只保留纯泰勒多项式
poly = sp.exp(x).series(x,0,4).removeO()
print(poly)  # 1 + x + x**2/2
```

## 三、分场景用法

### 场景 1：麦克劳林展开（中心点 $x_0=0$，矩母函数最常用）

对 $e^{tX}$ 关于 $t$ 在 0 点展开：

```python
t, X = sp.symbols("t X")
f = sp.exp(t * X)
# n=5：展开到 t^4 项，余项 O(t^5)
ser = f.series(t, 0, 5)
print(ser)
# 剥离余项，得到纯展开式
ser_pure = ser.removeO()
print(ser_pure)
```

输出纯展开：
$$1 + t X + \frac{t^2 X^2}{2} + \frac{t^3 X^3}{6} + \frac{t^4 X^4}{24}$$
和推导矩母函数 $M(t)=E(e^{tX})$ 用的泰勒展开完全一致。

### 场景 2：任意点泰勒展开（$x_0 \neq 0$）

把 $\sin(x)$ 在 $x=\pi/2$ 展开到 3 阶：

```python
x = sp.Symbol("x")
sp.sin(x).series(x, sp.pi/2, 4)
```

输出所有项都是 $(x-\pi/2)$ 的幂次，余项 $\mathcal{O}\left(\left(x-\tfrac{\pi}{2}\right)^4\right)$。

### 场景 3：只提取某一阶系数

```python
expr = sp.exp(x).series(x,0,6).removeO()
# 提取 x^3 项的系数
expr.coeff(x, 3)  # 输出 1/6
```

## 四、关键细节（容易踩坑）

1. **阶数参数 `n` 的逻辑**
   `series(var, x0, n)` 展开最高次是 $\boldsymbol{n-1}$，余项是 $n$ 阶。
   例：`n=3` → 最高 $x^2$，余项 $\mathcal{O}(x^3)$。

2. **只能单变量逐次展开**
   二元函数不能一次双变量泰勒，要分层调用 `series()`：

```python
x, y = sp.symbols("x y")
f = sp.exp(x + y)
# 先展开 x，去掉余项，再展开 y
res = f.series(x,0,3).removeO().series(y,0,3).removeO()
```

3. **只有佩亚诺余项，无自动拉格朗日余项**
   `series()` 只会输出 $\mathcal{O}(\cdot)$ 形式，不会自动生成带中间点 $\xi$ 的拉格朗日余项；需要手动求高阶导数构造。

4. 区分 `series()` 和 `sp.series()`
   两种写法等价：

```python
# 方法调用形式（推荐）
sp.exp(x).series(x, 0, 4)
```

```python
# 全局函数形式
sp.series(sp.exp(x), x, 0, 4)
```

## 五、和你之前知识串联

1. 数学上：`series()` 输出 = **完整带佩亚诺余项的泰勒公式**；
2. 去掉 `.removeO()` 后 = 纯泰勒展开多项式；
3. 矩母函数推导时，我们只用剥离余项后的无穷截断展开式，正好对应 `series().removeO()` 的结果。

## 六、极简记忆

`series(变量, 中心点, 截断阶n)`
= 在中心点做泰勒展开，写到 $(\text{变量}-x_0)^{n-1}$，末尾自带佩亚诺余项 $\mathcal{O}((\text{变量}-x_0)^n)$。
