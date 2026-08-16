---
title: Conditional Types
layout: docs
permalink: /docs/handbook/2/conditional-types.html
oneline: "Create types which act like if statements in the type system."
---

:::block
[en]
At the heart of most useful programs, we have to make decisions based on input.
JavaScript programs are no different, but given the fact that values can be easily introspected, those decisions are also based on the types of the inputs.
_Conditional types_ help describe the relation between the types of inputs and outputs.
[zh]
在大多数实用的程序中，我们必须根据输入做出决策。
JavaScript 程序也是如此，但鉴于值可以很容易地被内省，这些决策也基于输入的类型。
_条件类型_ 帮助描述输入和输出类型之间的关系。
:::

```ts twoslash
interface Animal {
  live(): void;
}
interface Dog extends Animal {
  woof(): void;
}

type Example1 = Dog extends Animal ? number : string;
//   ^?

type Example2 = RegExp extends Animal ? number : string;
//   ^?
```

:::block
[en]
Conditional types take a form that looks a little like conditional expressions (`condition ? trueExpression : falseExpression`) in JavaScript:
[zh]
条件类型 的形式看起来有点像 JavaScript 中的条件表达式（`condition ? trueExpression : falseExpression`）：
:::

```ts twoslash
type SomeType = any;
type OtherType = any;
type TrueType = any;
type FalseType = any;
type Stuff =
  // ---cut---
  SomeType extends OtherType ? TrueType : FalseType;
```

:::block
[en]
When the type on the left of the `extends` is assignable to the one on the right, then you'll get the type in the first branch (the "true" branch); otherwise you'll get the type in the latter branch (the "false" branch).
[zh]
当 `extends` 左侧的类型可分配给右侧的类型时，你将获得第一个分支（“true” 分支）中的类型；否则你将获得后一个分支（“false” 分支）中的类型。
:::

:::block
[en]
From the examples above, conditional types might not immediately seem useful - we can tell ourselves whether or not `Dog extends Animal` and pick `number` or `string`!
But the power of conditional types comes from using them with generics.
[zh]
从上面的例子来看，条件类型 可能不会立即显得有用 —— 我们自己就能知道 `Dog extends Animal` 是否成立，并选择 `number` 或 `string`！
但 条件类型 的强大之处在于将它们与泛型结合使用。
:::

:::block
[en]
For example, let's take the following `createLabel` function:
[zh]
例如，让我们来看看以下 `createLabel` 函数：
:::

```ts twoslash
interface IdLabel {
  id: number /* some fields */;
}
interface NameLabel {
  name: string /* other fields */;
}

function createLabel(id: number): IdLabel;
function createLabel(name: string): NameLabel;
function createLabel(nameOrId: string | number): IdLabel | NameLabel;
function createLabel(nameOrId: string | number): IdLabel | NameLabel {
  throw "unimplemented";
}
```

:::block
[en]
These overloads for createLabel describe a single JavaScript function that makes a choice based on the types of its inputs. Note a few things:
[zh]
这些用于 createLabel 的 重载 描述了一个根据其输入类型进行选择的单个 JavaScript 函数。注意以下几点：
:::

:::block
[en]
1. If a library has to make the same sort of choice over and over throughout its API, this becomes cumbersome.
2. We have to create three overloads: one for each case when we're _sure_ of the type (one for `string` and one for `number`), and one for the most general case (taking a `string | number`). For every new type `createLabel` can handle, the number of overloads grows exponentially.
[zh]
1. 如果一个库在其整个 API 中必须一遍又一遍地做出相同的选择，这会变得非常繁琐。
2. 我们必须创建三个 重载：当我们可以 _确定_ 类型时的每种情况各一个（一个用于 `string`，一个用于 `number`），以及最通用情况的一个（接受 `string | number`）。对于 `createLabel` 可以处理的每个新类型，重载 的数量都会呈指数增长。
:::

:::block
[en]
Instead, we can encode that logic in a conditional type:
[zh]
相反，我们可以将该逻辑编码在一个 条件类型 中：
:::

```ts twoslash
interface IdLabel {
  id: number /* some fields */;
}
interface NameLabel {
  name: string /* other fields */;
}
// ---cut---
type NameOrId<T extends number | string> = T extends number
  ? IdLabel
  : NameLabel;
```

:::block
[en]
We can then use that conditional type to simplify our overloads down to a single function with no overloads.
[zh]
然后，我们可以使用该 条件类型 将我们的 重载 简化为一个没有 重载 的单一函数。
:::

```ts twoslash
interface IdLabel {
  id: number /* some fields */;
}
interface NameLabel {
  name: string /* other fields */;
}
type NameOrId<T extends number | string> = T extends number
  ? IdLabel
  : NameLabel;
// ---cut---
function createLabel<T extends number | string>(idOrName: T): NameOrId<T> {
  throw "unimplemented";
}

let a = createLabel("typescript");
//  ^?

let b = createLabel(2.8);
//  ^?

let c = createLabel(Math.random() ? "hello" : 42);
//  ^?
```

:::block
[en]
## Conditional Type Constraints
[zh]
## 条件类型约束
:::

:::block
[en]
Often, the checks in a conditional type will provide us with some new information.
Just like narrowing with type guards can give us a more specific type, the true branch of a conditional type will further constrain generics by the type we check against.
[zh]
通常，条件类型 中的检查会为我们提供一些新信息。
就像使用类型守卫（type guards）收窄可以得到更具体的类型一样，条件类型 的 true 分支会通过我们检查的类型进一步约束泛型。
:::

:::block
[en]
For example, let's take the following:
[zh]
例如，让我们来看看以下内容：
:::

```ts twoslash
// @errors: 2339
type MessageOf<T> = T["message"];
```

:::block
[en]
In this example, TypeScript errors because `T` is not known to have a property called `message`.
We could constrain `T`, and TypeScript would no longer complain:
[zh]
在这个例子中，TypeScript 报错，因为 `T` 未被确定具有名为 `message` 的属性。
我们可以约束 `T`，这样 TypeScript 就不会再报错了：
:::

```ts twoslash
type MessageOf<T extends { message: unknown }> = T["message"];

interface Email {
  message: string;
}

type EmailMessageContents = MessageOf<Email>;
//   ^?
```

:::block
[en]
However, what if we wanted `MessageOf` to take any type, and default to `never` if a `message` property wasn't available?
We can do this by moving the constraint out and introducing a conditional type:
[zh]
然而，如果我们想让 `MessageOf` 接受 any 类型，并且在 `message` 属性不可用时默认返回 `never` 呢？
我们可以通过将约束移出并引入一个 条件类型 来做到这一点：
:::

```ts twoslash
type MessageOf<T> = T extends { message: unknown } ? T["message"] : never;

interface Email {
  message: string;
}

interface Dog {
  bark(): void;
}

type EmailMessageContents = MessageOf<Email>;
//   ^?

type DogMessageContents = MessageOf<Dog>;
//   ^?
```

:::block
[en]
Within the true branch, TypeScript knows `T` _will_ have a `message` property.
[zh]
在 true 分支内，TypeScript 知道 `T` _一定_ 会有 `message` 属性。
:::

:::block
[en]
As another example, we could also create a type called `Flatten` that flattens array types to their element types, but leaves them alone otherwise:
[zh]
作为另一个例子，我们还可以创建一个名为 `Flatten` 的类型，它将数组类型扁平化为它们的元素类型，否则保持原样：
:::

```ts twoslash
type Flatten<T> = T extends any[] ? T[number] : T;

// Extracts the element type.
type Str = Flatten<string[]>;
//   ^?

// Leaves the type alone.
type Num = Flatten<number>;
//   ^?
```

:::block
[en]
When `Flatten` is given an array type, it uses an indexed access with `number` to fetch the `string[]`'s element type.
Otherwise, it just returns the type it was given.
[zh]
当给 `Flatten` 传入一个数组类型时，它会使用 `number` 进行索引访问，以获取 `string[]` 的元素类型。
否则，它只返回传入的类型。
:::

:::block
[en]
## Inferring Within Conditional Types
[zh]
## 在条件类型中推断
:::

:::block
[en]
Conditional types provide us with a way to infer from types we compare against in the true branch using the `infer` keyword.
For example, we could have inferred the element type in `Flatten` instead of fetching it "manually" with an indexed access type:
[zh]
条件类型 为我们提供了一种在 true 分支中，使用 `infer` 关键字从与之比较的类型中进行 infer 的方法。
例如，我们本可以 infer `Flatten` 中的元素类型，而不是通过索引访问类型“手动”获取它：
:::

```ts twoslash
type Flatten<Type> = Type extends Array<infer Item> ? Item : Type;
```

:::block
[en]
Here, we used the `infer` keyword to declaratively introduce a new generic type variable named `Item` instead of specifying how to retrieve the element type of `Type` within the true branch.
This frees us from having to think about how to dig through and probing the structure of the types we're interested in.
[zh]
在这里，我们使用 `infer` 关键字声明式地引入了一个名为 `Item` 的新泛型类型变量，而不是在 true 分支内指定如何获取 `Type` 的元素类型。
这使我们无需再去思考如何挖掘和探测我们所关注的类型的结构。
:::

:::block
[en]
We can write some useful helper type aliases using the `infer` keyword.
For example, for simple cases, we can extract the return type of a function type:
[zh]
我们可以使用 `infer` 关键字编写一些有用的辅助类型别名。
例如，在简单的情况下，我们可以提取一个函数类型的返回类型：
:::

```ts twoslash
type GetReturnType<Type> = Type extends (...args: any[]) => infer Return
  ? Return
  : any;

type Num = GetReturnType<() => number>;
//   ^?

type Str = GetReturnType<(x: string) => string>;
//   ^?

type Bools = GetReturnType<(a: boolean, b: boolean) => boolean[]>;
//   ^?
```

:::block
[en]
When inferring from a type with multiple call signatures (such as the type of an overloaded function), inferences are made from the *last* signature (which, presumably, is the most permissive catch-all case). It is not possible to perform overload resolution based on a list of argument types.
[zh]
当从具有多个调用签名的类型（例如重载函数的类型）中进行 infer 时，推断 将从 * 最后一个 * 签名中做出（据推测，这是最宽泛的捕获所有情况的签名）。无法根据参数类型列表进行重载解析。
:::

```ts twoslash
declare function stringOrNum(x: string): number;
declare function stringOrNum(x: number): string;
declare function stringOrNum(x: string | number): string | number;

type T1 = GetReturnType<typeof stringOrNum>;
//   ^?
```

:::block
[en]
## Distributive Conditional Types
[zh]
## 分布式条件类型
:::

:::block
[en]
When conditional types act on a generic type, they become *distributive* when given a union type.
For example, take the following:
[zh]
当 条件类型 作用于泛型类型时，如果传入联合类型，它们就会变成 * 分布式 * 的。
例如，看下面的例子：
:::

```ts twoslash
type ToArray<Type> = Type extends any ? Type[] : never;
```

:::block
[en]
If we plug a union type into `ToArray`:
[zh]
如果我们将一个联合类型传入 `ToArray`：
:::

```ts twoslash
type ToArray<Type> = Type extends any ? Type[] : never;
// ---cut---
type StrArrOrNumArr = ToArray<string | number>;
//   ^?
```

:::block
[en]
what happens is that `ToArray` distributes on each member type of the union and maps that to the equivalent of:
[zh]
实际发生的是，`ToArray` 会分发到联合类型的每个成员类型上，并将其映射为等同于：
:::

```ts
  ToArray<string> | ToArray<number>;
```

:::block
[en]
which leaves us with:
[zh]
这使我们得到：
:::

```ts twoslash
type StrArrOrNumArr =
  // ---cut---
  string[] | number[];
```

:::block
[en]
Typically, distributivity is the desired behavior.
To avoid that behavior, you can surround each side of the `extends` keyword with square brackets.
[zh]
通常，分布式是预期的行为。
为了避免该行为，你可以用方括号包围 `extends` 关键字的两侧。
:::

```ts twoslash
type ToArrayNonDist<Type> = [Type] extends [any] ? Type[] : never;

// 'ArrOfStrOrNum' is no longer a union.
type ArrOfStrOrNum = ToArrayNonDist<string | number>;
//   ^?
```
