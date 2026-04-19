---
mainfont: SimSun
---

# 确定性推理练习

## 谓词逻辑公式化为子句集

1. $\forall x (P(x) \rightarrow \exists y Q(x, y))$

   $$
   \begin{align*}
   &\iff \forall x (\neg P(x) \lor \exists y Q(x, y)) \\
   &\iff \forall x (\neg P(x) \lor Q(x, f(x))) \\
   &\iff \neg P(x) \lor Q(x, f(x)) \\
   &\iff \{ \neg P(x) \lor Q(x, f(x)) \}
   \end{align*}
   $$

2. $\exists x \forall y (R(x, y) \rightarrow \neg S(y))$

   $$
   \begin{align*}
   &\iff \exists x \forall y (\neg R(x, y) \lor \neg S(y)) \\
   &\iff \forall y (\neg R(f(), y) \lor \neg S(y)) \\
   &\iff \neg R(f(), y) \lor \neg S(y) \\
   &\iff \{ \neg R(f(), y) \lor \neg S(y) \} \\
   \end{align*}
   $$

3. $\forall x (P(x) \land \exists y (Q(y) \rightarrow R(x, y)))$

   $$
   \begin{align*}
   &\iff \forall x (P(x) \land \exists y (\neg Q(y) \lor R(x, y))) \\
   &\iff \forall x (P(x) \land (\neg Q(f(x)) \lor R(x, f(x)))) \\
   &\iff P(x) \land (\neg Q(f(x)) \lor R(x, f(x))) \\
   &\iff \{ P(x), \neg Q(f(x)) \lor R(x, f(x)) \} \\
   &\iff \{ P(x), \neg Q(f(y)) \lor R(y, f(y)) \} \\
   \end{align*}
   $$

4. $\neg \forall x (\neg P(x) \lor \exists y T(x, y))$

   $$
   \begin{align*}
   &\iff \exists x (P(x) \land \forall y \neg T(x, y)) \\
   &\iff P(f()) \land \forall y \neg T(f(), y) \\
   &\iff P(f()) \land (\neg T(f(), y)) \\
   &\iff \{ P(f()), \neg T(f(), y) \} \\
   \end{align*}
   $$

5. $\forall x (F(x) \rightarrow (\exists y G(x, y) \land \forall z (G(x, z) \rightarrow H(z))))$

   $$
   \begin{align*}
   &\iff \forall x \neg F(x) \lor (\exists y G(x, y) \land \forall z (\neg G(x, z) \lor H(z))) \\
   &\iff \forall x \neg F(x) \lor (G(x, f(x)) \land \forall z (\neg G(x, z) \lor H(z))) \\
   &\iff \neg F(x) \lor (G(x, f(x)) \land (\neg G(x, z) \lor H(z))) \\
   &\iff \neg F(x) \lor G(x, f(x)) \land \neg F(x) \lor \neg G(x, z) \lor H(z) \\
   &\iff \{ \neg F(x) \lor G(x, f(x)), \neg F(x) \lor \neg G(x, z) \lor H(z) \} \\
   &\iff \{ \neg F(x) \lor G(x, f(x)), \neg F(y) \lor \neg G(y, z) \lor H(z) \} \\
   \end{align*}
   $$

6. $\forall x (A(x) \rightarrow \exists y (B(y) \land (C(x, y) \rightarrow \forall z D(y, z))))$

   $$
   \begin{align*}
   &\iff \forall x (\neg A(x) \lor \exists y (B(y) \land (\neg C(x, y) \lor \forall z D(y, z)))) \\
   &\iff \forall x (\neg A(x) \lor (B(f(x)) \land (\neg C(x, f(x)) \lor \forall z D(f(x), z)))) \\
   &\iff \neg A(x) \lor (B(f(x)) \land (\neg C(x, f(x)) \lor D(f(x), z))) \\
   &\iff \neg A(x) \lor B(f(x)) \land \neg A(x) \lor \neg C(x, f(x)) \lor D(f(x), z) \\
   &\iff \{ \neg A(x) \lor B(f(x)), \neg A(x) \lor \neg C(x, f(x)) \lor D(f(x), z) \} \\
   &\iff \{ \neg A(x) \lor B(f(x)), \neg A(y) \lor \neg C(y, f(y)) \lor D(f(y), z) \} \\
   \end{align*}
   $$

7. $\neg \exists x \forall y (P(y) \rightarrow (Q(x, y) \lor \exists z \neg R(y, z)))$

   $$
   \begin{align*}
   &\iff \neg \exists x \forall y (\neg P(y) \lor (Q(x, y) \lor \exists z \neg R(y, z))) \\
   &\iff \forall x \exists y (P(y) \land (\neg Q(x, y) \land \forall z R(y, z))) \\
   &\iff \forall x (P(f(x)) \land (\neg Q(x, f(x)) \land \forall z R(f(x), z))) \\
   &\iff P(f(x)) \land \neg Q(x, f(x)) \land z R(f(x), z) \\
   &\iff \{ P(f(x)), \neg Q(x, f(x)), z R(f(x), z) \} \\
   &\iff \{ P(f(x)), \neg Q(y, f(y)), z R(f(w), z) \} \\
   \end{align*}
   $$

### 程序验证

<https://github.com/ForkKILLET/FkAIHomework/tree/main/ClauseSet>

## 使用归结反演证明

1. 前提：
   - 所有爱猫的人都不喜欢老鼠
   - 有人爱猫
   - 如果某人不喜欢老鼠，他就不会养老鼠

   求证：存在某人，他不养老鼠

   **证明**：

   设 $P(x)$ 表示“$x$ 爱猫”，$Q(x)$ 表示“$x$ 喜欢老鼠”，$R(x)$ 表示“$x$ 养老鼠”。

   前提：

   $$
   \begin{align*}
   (1)& \quad \forall x. P(x) \rightarrow \neg Q(x) \\
   (2)& \quad \exists x. P(x) \\
   (3)& \quad \forall x. \neg Q(x) \rightarrow \neg R(x)
   \end{align*}
   $$

   结论的否定：

   $$
   (4) \quad \neg \exists x. \neg R(x)
   $$

   子句集：

   $$
   \begin{align*}
   (1)& \quad \neg P(x) \lor \neg Q(x) \\
   (2)& \quad P(f()) \\
   (3)& \quad Q(x) \lor \neg R(x) \\
   (4)& \quad R(x) 
   \end{align*}
   $$

   归结：

   $$
   \begin{align*}
   (1), (3) \implies (5)& \quad \neg P(x) \lor \neg R(x) \\
   (4), (5) \implies (6)& \quad \neg P(x) \\
   (2), (6) \implies (7)& \quad \bot
   \end{align*}
   $$

   因此，结论成立。