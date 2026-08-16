---
title: The Basics
layout: docs
permalink: /docs/handbook/2/basic-types.html
oneline: "Step one in learning TypeScript: The basic types."
preamble: >
  <p>Welcome to the first page of the handbook. If this is your first experience with TypeScript - you may want to start at one of the '<a href='https://www.typescriptlang.org/docs/handbook/intro.html#get-started'>Getting Started</a>' guides</a>
---

:::block
[en]
Each and every value in JavaScript has a set of behaviors you can observe from running different operations.
That sounds abstract, but as a quick example, consider some operations we might run on a variable named `message`.
[zh]
JavaScript 中的每一个值在运行不同的操作时都有一组可以观察到的行为。
这听起来很抽象，但作为一个快速的例子，考虑我们可能在一个名为 `message` 的变量上运行的一些操作。
:::

```js
// Accessing the property 'toLowerCase'
// on 'message' and then calling it
message.toLowerCase();

// Calling 'message'
message();
```

:::block
[en]
If we break this down, the first runnable line of code accesses a property called `toLowerCase` and then calls it.
The second one tries to call `message` directly.
[zh]
如果我们把这分解开来，第一行可运行的代码访问了一个名为 `toLowerCase` 的属性，然后调用了它。
第二行代码尝试直接调用 `message`。
:::

:::block
[en]
But assuming we don't know the value of `message` - and that's pretty common - we can't reliably say what results we'll get from trying to run any of this code.
The behavior of each operation depends entirely on what value we had in the first place.
[zh]
但是假设我们不知道 `message` 的值——这非常常见——我们无法可靠地预测运行这些代码会得到什么结果。
每个操作的行为完全取决于我们最初拥有什么值。
:::

:::block
[en]
- Is `message` callable?
- Does it have a property called `toLowerCase` on it?
- If it does, is `toLowerCase` even callable?
- If both of these values are callable, what do they return?
[zh]
- `message` 是可调用的吗？
- 它上面有一个名为 `toLowerCase` 的属性吗？
- 如果有，`toLowerCase` 甚至是可调用的吗？
- 如果这两个值都是可调用的，它们返回什么？
:::

:::block
[en]
The answers to these questions are usually things we keep in our heads when we write JavaScript, and we have to hope we got all the details right.
[zh]
当我们编写 JavaScript 时，这些问题的答案通常是保存在我们的脑海中的，我们必须寄希望于自己把所有的细节都弄对了。
:::

:::block
[en]
Let's say `message` was defined in the following way.
[zh]
假设 `message` 是以下面这种方式定义的。
:::

```js
const message = "Hello World!";
```

:::block
[en]
As you can probably guess, if we try to run `message.toLowerCase()`, we'll get the same string only in lower-case.
[zh]
正如你可能猜到的，如果我们尝试运行 `message.toLowerCase()`，我们将得到相同的 string，只不过它是小写的。
:::

:::block
[en]
What about that second line of code?
If you're familiar with JavaScript, you'll know this fails with an exception:
[zh]
那第二行代码呢？
如果你熟悉 JavaScript，你就会知道这会失败并抛出一个异常：
:::

```txt
TypeError: message is not a function
```

:::block
[en]
It'd be great if we could avoid mistakes like this.
[zh]
如果能避免这样的错误就太好了。
:::

:::block
[en]
When we run our code, the way that our JavaScript runtime chooses what to do is by figuring out the _type_ of the value - what sorts of behaviors and capabilities it has.
That's part of what that `TypeError` is alluding to - it's saying that the string `"Hello World!"` cannot be called as a function.
[zh]
当我们运行代码时，JavaScript 运行时决定做什么的方法是通过弄清楚值的 _type_——即它具有什么样的行为和能力。这就是 `TypeError` 所暗示的部分内容——它在说明 string `"Hello World!"` 无法作为函数被调用。
:::

:::block
[en]
For some values, such as the primitives `string` and `number`, we can identify their type at runtime using the `typeof` operator.
But for other things like functions, there's no corresponding runtime mechanism to identify their types.
For example, consider this function:
[zh]
对于某些值，例如原始类型 `string` 和 `number`，我们可以在运行时使用 `typeof` 运算符来识别它们的类型。
但对于其他事物（如函数），则没有相应的运行时机制来识别它们的类型。
例如，考虑这个函数：
:::

```js
function fn(x) {
  return x.flip();
}
```

:::block
[en]
We can _observe_ by reading the code that this function will only work if given an object with a callable `flip` property, but JavaScript doesn't surface this information in a way that we can check while the code is running.
The only way in pure JavaScript to tell what `fn` does with a particular value is to call it and see what happens.
This kind of behavior makes it hard to predict what the code will do before it runs, which means it's harder to know what your code is going to do while you're writing it.
[zh]
我们通过阅读代码可以 _观察_ 到，这个函数只有在给定一个具有可调用 `flip` 属性的对象时才能工作，但 JavaScript 并没有以一种我们可以在代码运行时进行检查的方式来显露这种信息。
在纯 JavaScript 中，了解 `fn` 对特定值做什么的唯一方法就是调用它并看看会发生什么。
This kind of behavior makes it hard to predict what the code will do before it runs, which means it's harder to know what your code is going to do while you're writing it.
[zh]
我们通过阅读代码可以 _观察_ 到，这个函数只有在给定一个具有可调用 `flip` 属性的对象时才能工作，但 JavaScript 并没有以一种我们可以在代码运行时进行检查的方式来显露这种信息。
在纯 JavaScript 中，了解 `fn` 对特定值做什么的唯一方法就是调用它并看看会发生什么。
这种行为使得在代码运行之前很难预测它会做什么，这意味着在编写代码时，很难知道你的代码将会做什么。
:::

:::block
[en]
Seen in this way, a _type_ is the concept of describing which values can be passed to `fn` and which will crash.
JavaScript only truly provides _dynamic_ typing - running the code to see what happens.
[zh]
从这个角度来看，_type_ 是描述哪些值可以传递给 `fn` 以及哪些值会导致崩溃的概念。
JavaScript 仅真正提供了 _动态_ 类型——运行代码以查看会发生什么。
:::

:::block
[en]
The alternative is to use a _static_ type system to make predictions about what the code is expected to do _before_ it runs.
[zh]
另一种选择是使用 _静态_ 类型系统，在代码运行 _之前_ 预测其预期行为。
:::

:::block
[en]
## Static type-checking
[zh]
## 静态类型检查
:::

:::block
[en]
Think back to that `TypeError` we got earlier from trying to call a `string` as a function.
_Most people_ don't like to get any sorts of errors when running their code - those are considered bugs!
And when we write new code, we try our best to avoid introducing new bugs.
[zh]
回想一下我们之前尝试将 `string` 作为函数调用时得到的 `TypeError`。
_大多数人_ 都不喜欢在运行代码时遇到任何形式的错误——那些被认为是 bug！
当我们编写新代码时，我们会尽最大努力避免引入新的 bug。
:::

:::block
[en]
If we add just a bit of code, save our file, re-run the code, and immediately see the error, we might be able to isolate the problem quickly; but that's not always the case.
We might not have tested the feature thoroughly enough, so we might never actually run into a potential error that would be thrown!
Or if we were lucky enough to witness the error, we might have ended up doing large refactorings and adding a lot of different code that we're forced to dig through.
[zh]
如果我们只添加了一点点代码，保存文件，重新运行代码，然后立即看到错误，我们也许能够快速定位问题；但这并不总是发生。
我们可能没有足够彻底地测试该功能，因此我们实际上可能永远不会遇到将被抛出的潜在错误！
或者，如果我们足够幸运地目睹了该错误，我们可能已经完成了大型重构并添加了许多不同的代码，导致我们不得不去艰难排查。
:::

:::block
[en]
Ideally, we could have a tool that helps us find these bugs _before_ our code runs.
That's what a static type-checker like TypeScript does.
_Static type systems_ describe the shapes and behaviors of what our values will be when we run our programs.
A type-checker like TypeScript uses that information and tells us when things might be going off the rails.
[zh]
理想情况下，我们可以有一个工具来帮助我们在代码运行 _之前_ 找到这些 bug。
这就是像 TypeScript 这样的静态类型检查器所做的工作。
_静态类型系统_ 描述了我们在运行程序时值的形状和行为。
像 TypeScript 这样的类型检查器会使用这些信息，并在事情可能偏离正轨时告诉我们。
:::

```ts twoslash
// @errors: 2349
const message = "hello!";

message();
```

:::block
[en]
Running that last sample with TypeScript will give us an error message before we run the code in the first place.
[zh]
使用 TypeScript 运行上一个示例，甚至在我们运行代码之前，就会给我们一个错误提示。
:::

:::block
[en]
## Non-exception Failures
[zh]
## 非异常的失败
:::

:::block
[en]
So far we've been discussing certain things like runtime errors - cases where the JavaScript runtime tells us that it thinks something is nonsensical.
Those cases come up because [the ECMAScript specification](https://tc39.github.io/ecma262/) has explicit instructions on how the language should behave when it runs into something unexpected.
[zh]
到目前为止，我们一直在讨论诸如运行时错误之类的事情——即 JavaScript 运行时告诉我们它认为某些东西是没有意义的。
出现这些情况是因为 [ECMAScript 规范](https://tc39.github.io/ecma262/) 对于语言在遇到意外情况时应该如何表现有明确的说明。
:::

:::block
[en]
For example, the specification says that trying to call something that isn't callable should throw an error.
Maybe that sounds like "obvious behavior", but you could imagine that accessing a property that doesn't exist on an object should throw an error too.
Instead, JavaScript gives us different behavior and returns the value `undefined`:
[zh]
例如，规范中指出，尝试调用不可调用的内容应该抛出错误。
这听起来可能是“显而易见的行为”，但你也可以想象，访问对象上不存在的属性也应该抛出错误。
相反，JavaScript 给我们提供了不同的行为，并返回了值 `undefined`：
:::

```js
const user = {
  name: "Daniel",
  age: 26,
};

user.location; // returns undefined
```

:::block
[en]
Ultimately, a static type system has to make the call over what code should be flagged as an error in its system, even if it's "valid" JavaScript that won't immediately throw an error.
In TypeScript, the following code produces an error about `location` not being defined:
[zh]
最终，静态类型系统必须决定在其系统中应该将哪些代码标记为错误，即使它是不会立即抛出错误的“有效” JavaScript。
在 TypeScript 中，以下代码会产生一个关于 `location` 未定义的错误：
:::

```ts twoslash
// @errors: 2339
const user = {
  name: "Daniel",
  age: 26,
};

user.location;
```

:::block
[en]
While sometimes that implies a trade-off in what you can express, the intent is to catch legitimate bugs in our programs.
And TypeScript catches _a lot_ of legitimate bugs.
[zh]
虽然这有时意味着在你所能表达的内容上有所权衡，但其意图是捕获我们程序中的真实 bug。
而且 TypeScript 捕获了 _很多_ 真实的 bug。
:::

:::block
[en]
For example: typos,
[zh]
例如：拼写错误，
:::

```ts twoslash
// @noErrors
const announcement = "Hello World!";

// How quickly can you spot the typos?
announcement.toLocaleLowercase();
announcement.toLocalLowerCase();

// We probably meant to write this...
announcement.toLocaleLowerCase();
```

:::block
[en]
uncalled functions,
[zh]
未调用的函数，
:::

```ts twoslash
// @noUnusedLocals
// @errors: 2365
function flipCoin() {
  // Meant to be Math.random()
  return Math.random < 0.5;
}
```

:::block
[en]
or basic logic errors.
[zh]
或者基本的逻辑错误。
:::

```ts twoslash
// @errors: 2367
const value = Math.random() < 0.5 ? "a" : "b";
if (value !== "a") {
  // ...
} else if (value === "b") {
  // Oops, unreachable
}
```

:::block
[en]
## Types for Tooling
[zh]
## 类型与工具
:::

:::block
[en]
TypeScript can catch bugs when we make mistakes in our code.
That's great, but TypeScript can _also_ prevent us from making those mistakes in the first place.
[zh]
当我们在代码中犯错时，TypeScript 可以捕获 bug。
这很好，但 TypeScript _也可以_ 在一开始就阻止我们犯这些错误。
:::

:::block
[en]
The type-checker has information to check things like whether we're accessing the right properties on variables and other properties.
Once it has that information, it can also start _suggesting_ which properties you might want to use.
[zh]
类型检查器拥有所需的信息，以检查我们是否访问了变量以及其他属性上的正确属性。
一旦它拥有了这些信息，它也可以开始 _建议_ 你可能想要使用哪些属性。
:::

:::block
[en]
That means TypeScript can be leveraged for editing code too, and the core type-checker can provide error messages and code completion as you type in the editor.
That's part of what people often refer to when they talk about tooling in TypeScript.
[zh]
这意味着 TypeScript 也可以用来辅助编辑代码，核心类型检查器可以在你在编辑器中输入时提供错误消息和代码补全。
这就是人们在谈论 TypeScript 中的工具支持时经常提到的一部分内容。
:::

:::block
[en]
<!-- prettier-ignore -->
[zh]
<!-- prettier-ignore -->
:::

```ts twoslash
// @noErrors
// @esModuleInterop
import express from "express";
const app = express();

app.get("/", function (req, res) {
  res.sen
//       ^|
});

app.listen(3000);
```

:::block
[en]
TypeScript takes tooling seriously, and that goes beyond completions and errors as you type.
An editor that supports TypeScript can deliver "quick fixes" to automatically fix errors, refactorings to easily re-organize code, and useful navigation features for jumping to definitions of a variable, or finding all references to a given variable.
All of this is built on top of the type-checker and is fully cross-platform, so it's likely that [your favorite editor has TypeScript support available](https://github.com/Microsoft/TypeScript/wiki/TypeScript-Editor-Support).
[zh]
TypeScript 非常重视工具支持，而且这不仅仅局限于输入时的补全和错误提示。
支持 TypeScript 的编辑器可以提供“快速修复”以自动修复错误、重构以轻松重新组织代码，以及有用的导航功能，用于跳转到变量的定义或查找对给定变量的所有引用。
所有这些都是构建在类型检查器之上的，并且完全跨平台，因此 [你最喜欢的编辑器很可能已经提供了对 TypeScript 的支持](https://github.com/Microsoft/TypeScript/wiki/TypeScript-Editor-Support)。
:::

:::block
[en]
## `tsc`, the TypeScript compiler
[zh]
## `tsc`，TypeScript 编译器
:::

:::block
[en]
We've been talking about type-checking, but we haven't yet used our type-_checker_.
Let's get acquainted with our new friend `tsc`, the TypeScript compiler.
First we'll need to grab it via npm.
[zh]
我们一直在谈论类型检查，但我们还没有使用我们的类型 _检查器_。
让我们来结识我们的新朋友 `tsc`，即 TypeScript 编译器。
首先，我们需要通过 npm 获取它。
:::

```sh
npm install -g typescript
```

:::block
[en]
> This installs the TypeScript Compiler `tsc` globally.
> You can use `npx` or similar tools if you'd prefer to run `tsc` from a local `node_modules` package instead.
[zh]
> 这将全局安装 TypeScript 编译器 `tsc`。
> 如果你更愿意从本地的 `node_modules` 包中运行 `tsc`，你可以使用 `npx` 或类似的工具。
:::

:::block
[en]
Now let's move to an empty folder and try writing our first TypeScript program: `hello.ts`:
[zh]
现在，让我们进入一个空文件夹，并尝试编写我们的第一个 TypeScript 程序：`hello.ts`：
:::

```ts twoslash
// Greets the world.
console.log("Hello world!");
```

:::block
[en]
Notice there are no frills here; this "hello world" program looks identical to what you'd write for a "hello world" program in JavaScript.
And now let's type-check it by running the command `tsc` which was installed for us by the `typescript` package.
[zh]
注意这里没有任何花哨的地方；这个“hello world”程序看起来与你在 JavaScript 中编写的“hello world”程序完全相同。
现在让我们通过运行由 `typescript` 包为我们安装的 `tsc` 命令来进行类型检查。
:::

```sh
tsc hello.ts
```

:::block
[en]
Tada!
[zh]
哒哒！
:::

:::block
[en]
Wait, "tada" _what_ exactly?
We ran `tsc` and nothing happened!
Well, there were no type errors, so we didn't get any output in our console since there was nothing to report.
[zh]
等等，到底“哒哒”了 _什么_？
我们运行了 `tsc`，但什么也没发生！
好吧，因为没有类型错误，所以我们的控制台中没有任何输出，因为没有什么需要报告的。
:::

:::block
[en]
But check again - we got some _file_ output instead.
If we look in our current directory, we'll see a `hello.js` file next to `hello.ts`.
That's the output from our `hello.ts` file after `tsc` _compiles_ or _transforms_ it into a plain JavaScript file.
And if we check the contents, we'll see what TypeScript spits out after it processes a `.ts` file:
[zh]
但再检查一下——我们实际上得到了一个 _文件_ 输出。
如果我们查看当前目录，我们会看到 `hello.ts` 旁边多了一个 `hello.js` 文件。
这就是 `tsc` 将我们的 `hello.ts` 文件 _编译_ 或 _转换_ 为纯 JavaScript 文件后的输出。
如果我们查看其中的内容，我们将看到 TypeScript 在处理 `.ts` 文件后输出的内容：
:::

```js
// Greets the world.
console.log("Hello world!");
```

:::block
[en]
In this case, there was very little for TypeScript to transform, so it looks identical to what we wrote.
The compiler tries to emit clean readable code that looks like something a person would write.
While that's not always so easy, TypeScript indents consistently, is mindful of when our code spans across different lines of code, and tries to keep comments around.
[zh]
在这种情况下，TypeScript 需要转换的内容非常少，所以它看起来和我们编写的代码完全相同。
编译器试图生成干净且可读的代码，就像人写的一样。
虽然这并不总是那么容易，但 TypeScript 的缩进是一致的，并且会注意到我们的代码何时跨越不同的代码行，并努力保留其中的注释。
:::

:::block
[en]
What about if we _did_ introduce a type-checking error?
Let's rewrite `hello.ts`:
[zh]
如果我们 _确实_ 引入了一个类型检查错误会怎么样？
让我们重写 `hello.ts`：
:::

```ts twoslash
// @noErrors
// This is an industrial-grade general-purpose greeter function:
function greet(person, date) {
  console.log(`Hello ${person}, today is ${date}!`);
}

greet("Brendan");
```

:::block
[en]
If we run `tsc hello.ts` again, notice that we get an error on the command line!
[zh]
如果我们再次运行 `tsc hello.ts`，注意我们会在命令行中得到一个错误！
:::

```txt
Expected 2 arguments, but got 1.
```

:::block
[en]
TypeScript is telling us we forgot to pass an argument to the `greet` function, and rightfully so.
So far we've only written standard JavaScript, and yet type-checking was still able to find problems with our code.
Thanks TypeScript!
[zh]
TypeScript 正在告诉我们，我们忘记给 `greet` 函数传递参数了，理应如此。
到目前为止，我们只编写了标准的 JavaScript，但类型检查仍然能够发现我们代码中的问题。
谢谢 TypeScript！
:::

:::block
[en]
## Emitting with Errors
[zh]
## 伴随错误的输出
:::

:::block
[en]
One thing you might not have noticed from the last example was that our `hello.js` file changed again.
If we open that file up then we'll see that the contents still basically look the same as our input file.
That might be a bit surprising given the fact that `tsc` reported an error about our code, but this is based on one of TypeScript's core values: much of the time, _you_ will know better than TypeScript.
[zh]
上一个例子中你可能没有注意到的一点是，我们的 `hello.js` 文件再次改变了。
如果我们打开那个文件，我们会看到内容基本上看起来仍然和我们的输入文件一样。
考虑到 `tsc` 报告了关于我们代码电错误，这可能会有点令人惊讶，但这基于 TypeScript 的核心价值观之一：在很多时候，_你_ 比 TypeScript 更清楚自己在做什么。
:::

:::block
[en]
To reiterate from earlier, type-checking code limits the sorts of programs you can run, and so there's a tradeoff on what sorts of things a type-checker finds acceptable.
Most of the time that's okay, but there are scenarios where those checks get in the way.
For example, imagine yourself migrating JavaScript code over to TypeScript and introducing type-checking errors.
Eventually you'll get around to cleaning things up for the type-checker, but that original JavaScript code was already working!
Why should converting it over to TypeScript stop you from running it?
[zh]
重申一下之前的内容，类型检查代码限制了你可以运行的程序种类，因此在类型检查器认为可接受的事情上存在权衡。
大多数时候这没问题，但在某些场景下，这些检查会成为阻碍。
例如，想象一下你自己将 JavaScript 代码迁移到 TypeScript 并引入了类型检查错误。
最终你会抽出时间来为类型检查器清理这些错误，但原来的 JavaScript 代码本就可以正常运行！
为什么将它转换到 TypeScript 会阻止你运行它呢？
:::

:::block
[en]
So TypeScript doesn't get in your way.
Of course, over time, you may want to be a bit more defensive against mistakes, and make TypeScript act a bit more strictly.
In that case, you can use the [`noEmitOnError`](/tsconfig#noEmitOnError) compiler option.
Try changing your `hello.ts` file and running `tsc` with that flag:
[zh]
因此，TypeScript 不会阻碍你。
当然，随着时间的推移，你可能希望对错误更具防备性，并让 TypeScript 表现得更严格一些。
在这种情况下，你可以使用 [`noEmitOnError`](/tsconfig#noEmitOnError) 编译器选项。
尝试修改你的 `hello.ts` 文件并运行带有该标志的 `tsc`：
:::

```sh
tsc --noEmitOnError hello.ts
```

:::block
[en]
You'll notice that `hello.js` never gets updated.
[zh]
你会注意到 `hello.js` 永远不会被更新。
:::

:::block
[en]
## Explicit Types
[zh]
## 显式类型
:::

:::block
[en]
Up until now, we haven't told TypeScript what `person` or `date` are.
Let's edit the code to tell TypeScript that `person` is a `string`, and that `date` should be a `Date` object.
We'll also use the `toDateString()` method on `date`.
[zh]
直到现在，我们还没有告诉 TypeScript `person` 或 `date` 是什么。
让我们编辑代码来告诉 TypeScript `person` 是一个 `string`，并且 `date` 应该是一个 `Date` 对象。
我们还会对 `date` 使用 `toDateString()` 方法。
:::

```ts twoslash
function greet(person: string, date: Date) {
  console.log(`Hello ${person}, today is ${date.toDateString()}!`);
}
```

:::block
[en]
What we did was add _type annotations_ on `person` and `date` to describe what types of values `greet` can be called with.
You can read that signature as "`greet` takes a `person` of type `string`, and a `date` of type `Date`".
[zh]
我们所做的是在 `person` 和 `date` 上添加 _类型注解_，以描述可以使用什么类型的参数来调用 `greet`。
你可以将该签名解读为“`greet` 接收一个 `string` 类型的 `person`，以及一个 `Date` 类型的 `date`”。
:::

:::block
[en]
With this, TypeScript can tell us about other cases where `greet` might have been called incorrectly.
For example...
[zh]
有了这个，TypeScript 就能告诉我们其他可能错误调用 `greet` 的情况。
例如...
:::

```ts twoslash
// @errors: 2345
function greet(person: string, date: Date) {
  console.log(`Hello ${person}, today is ${date.toDateString()}!`);
}

greet("Maddison", Date());
```

:::block
[en]
Huh?
TypeScript reported an error on our second argument, but why?
[zh]
嗯？
TypeScript 在我们的第二个参数上报告了一个错误，但这是为什么？
:::

:::block
[en]
Perhaps surprisingly, calling `Date()` in JavaScript returns a `string`.
On the other hand, constructing a `Date` with `new Date()` actually gives us what we were expecting.
[zh]
也许令人惊讶的是，在 JavaScript 中调用 `Date()` 会返回一个 `string`。
另一方面，使用 `new Date()` 构造一个 `Date` 实际上会给我们我们所期望的结果。
:::

:::block
[en]
Anyway, we can quickly fix up the error:
[zh]
无论如何，我们可以快速修复这个错误：
:::

```ts twoslash {4}
function greet(person: string, date: Date) {
  console.log(`Hello ${person}, today is ${date.toDateString()}!`);
}

greet("Maddison", new Date());
```

:::block
[en]
Keep in mind, we don't always have to write explicit type annotations.
In many cases, TypeScript can even just _infer_ (or "figure out") the types for us even if we omit them.
[zh]
记住，我们并不总是需要编写显式类型注解。
在许多情况下，即使我们省略了它们，TypeScript 甚至也可以直接为我们 _推断_（或“弄清楚”）类型。
:::

```ts twoslash
let msg = "hello there!";
//  ^?
```

:::block
[en]
Even though we didn't tell TypeScript that `msg` had the type `string` it was able to figure that out.
That's a feature, and it's best not to add annotations when the type system would end up inferring the same type anyway.
[zh]
即使我们没有告诉 TypeScript `msg` 的类型是 `string`，它也能够弄清楚这一点。
这是一个特性，当类型系统最终能够推断出相同的类型时，最好不要添加注解。
:::

:::block
[en]
> Note: The message bubble inside the previous code sample is what your editor would show if you had hovered over the word.
[zh]
> 注意：前一个代码示例中的消息气泡是当你的鼠标悬停在该单词上时编辑器所显示的内容。
:::

:::block
[en]
## Erased Types
[zh]
## 擦除的类型
:::

:::block
[en]
Let's take a look at what happens when we compile the above function `greet` with `tsc` to output JavaScript:
[zh]
让我们来看看当我们将上述的 `greet` 函数用 `tsc` 编译以输出 JavaScript 时会发生什么：
:::

```ts twoslash
// @showEmit
// @target: es5
function greet(person: string, date: Date) {
  console.log(`Hello ${person}, today is ${date.toDateString()}!`);
}

greet("Maddison", new Date());
```

:::block
[en]
Notice two things here:
[zh]
注意这里的两件事：
:::

:::block
[en]
1. Our `person` and `date` parameters no longer have type annotations.
2. Our "template string" - that string that used backticks (the `` ` `` character) - was converted to plain strings with concatenations.
[zh]
1. 我们的 `person` 和 `date` 参数不再有类型注解。
2. 我们的“模板字符串”——即使用反引号（ `` ` `` 字符）的字符串——被转换成了带有拼接的普通字符串。
:::

:::block
[en]
More on that second point later, but let's now focus on that first point.
Type annotations aren't part of JavaScript (or ECMAScript to be pedantic), so there really aren't any browsers or other runtimes that can just run TypeScript unmodified.
That's why TypeScript needs a compiler in the first place - it needs some way to strip out or transform any TypeScript-specific code so that you can run it.
Most TypeScript-specific code gets erased away, and likewise, here our type annotations were completely erased.
[zh]
稍后会详细介绍第二点，但现在让我们先专注于第一点。
类型注解并不是 JavaScript 的一部分（或者严格点说是 ECMAScript 的一部分），因此实际上没有任何浏览器或其他运行时可以直接运行未经修改的 TypeScript。
这就是为什么 TypeScript 首先需要一个编译器——它需要某种方法来剥离或转换任何 TypeScript 特定的代码，以便你可以运行它。
大多数 TypeScript 特定的代码都会被擦除，同样地，这里我们的类型注解也被完全擦除了。
:::

:::block
[en]
> **Remember**: Type annotations never change the runtime behavior of your program.
[zh]
> ** 记住 **：类型注解永远不会改变你程序的运行时行为。
:::

:::block
[en]
## Downleveling
[zh]
## 降级
:::

:::block
[en]
One other difference from the above was that our template string was rewritten from
[zh]
与上述内容相比，另一个不同之处在于我们的模板字符串被重写了，从
:::

```js
`Hello ${person}, today is ${date.toDateString()}!`;
```

:::block
[en]
to
[zh]
为
:::

```js
"Hello ".concat(person, ", today is ").concat(date.toDateString(), "!");
```

:::block
[en]
Why did this happen?
[zh]
为什么会发生这种情况？
:::

:::block
[en]
Template strings are a feature from a version of ECMAScript called ECMAScript 2015 (a.k.a. ECMAScript 6, ES2015, ES6, etc. - _don't ask_).
TypeScript has the ability to rewrite code from newer versions of ECMAScript to older ones such as ECMAScript 3 or ECMAScript 5 (a.k.a. ES5).
This process of moving from a newer or "higher" version of ECMAScript down to an older or "lower" one is sometimes called _downleveling_.
[zh]
模板字符串是来自一个名为 ECMAScript 2015 的 ECMAScript 版本的特性（又名 ECMAScript 6、ES2015、ES6 等——_别问_）。
TypeScript 有能力将新版本 ECMAScript 的代码重写为旧版本，例如 ECMAScript 3 或 ECMAScript 5（又名 ES5）。
这种从新版本或“高级”版本的 ECMAScript 移动到旧版本或“低级”版本的过程有时被称为 _降级_。
:::

:::block
[en]
By default TypeScript targets ES5, an extremely old version of ECMAScript.
We could have chosen something a little bit more recent by using the [`target`](/tsconfig#target) option.
Running with `--target es2015` changes TypeScript to target ECMAScript 2015, meaning code should be able to run wherever ECMAScript 2015 is supported.
So running `tsc --target es2015 hello.ts` gives us the following output:
[zh]
默认情况下，TypeScript 的目标是 ES5，这是一个非常古老的 ECMAScript 版本。
我们可以通过使用 [`target`](/tsconfig#target) 选项来选择一些稍微新一点的版本。
运行带 `--target es2015` 参数会改变 TypeScript 的目标为 ECMAScript 2015，这意味着代码应该能够在任何支持 ECMAScript 2015 的地方运行。
所以运行 `tsc --target es2015 hello.ts` 会给我们以下输出：
:::

```js
function greet(person, date) {
  console.log(`Hello ${person}, today is ${date.toDateString()}!`);
}
greet("Maddison", new Date());
```

:::block
[en]
> While the default target is ES5, the great majority of current browsers support ES2015.
> Most developers can therefore safely specify ES2015 or above as a target, unless compatibility with certain ancient browsers is important.
[zh]
> 虽然默认目标是 ES5，但目前绝大多数浏览器都支持 ES2015。
> 因此，除非与某些古老浏览器的兼容性非常重要，否则大多数开发人员可以安全地将 ES2015 或更高版本指定为目标。
:::

:::block
[en]
## Strictness
[zh]
## 严格度
:::

:::block
[en]
Different users come to TypeScript looking for different things in a type-checker.
Some people are looking for a more loose opt-in experience which can help validate only some parts of their program, and still have decent tooling.
This is the default experience with TypeScript, where types are optional, inference takes the most lenient types, and there's no checking for potentially `null`/`undefined` values.
Much like how `tsc` emits in the face of errors, these defaults are put in place to stay out of your way.
If you're migrating existing JavaScript, that might be a desirable first step.
[zh]
不同的用户来到 TypeScript，希望从类型检查器中获得不同的体验。
有些人正在寻找一种更宽松的选择性（opt-in）体验，这可以只帮助验证他们程序的某些部分，同时仍然拥有不错的工具支持。
这是 TypeScript 的默认体验，其中类型是可选的，推断会采用最宽松的类型，并且不会检查可能为 `null`/`undefined` 的值。
就像 `tsc` 在面对错误时依然会输出代码一样，这些默认设置是为了不阻碍你。
如果你正在迁移现有的 JavaScript，这可能是一个理想的第一步。
:::

:::block
[en]
In contrast, a lot of users prefer to have TypeScript validate as much as it can straight away, and that's why the language provides strictness settings as well.
These strictness settings turn static type-checking from a switch (either your code is checked or not) into something closer to a dial.
The further you turn this dial up, the more TypeScript will check for you.
This can require a little extra work, but generally speaking it pays for itself in the long run, and enables more thorough checks and more accurate tooling.
When possible, a new codebase should always turn these strictness checks on.
[zh]
相比之下，很多用户更喜欢让 TypeScript 立即尽可能多地进行验证，这也是为什么该语言也提供了严格度设置。
这些严格度设置将静态类型检查从一个开关（要么检查你的代码，要么不检查）变成了更类似于刻度盘的东西。
你把这个刻度盘拨得越高，TypeScript 为你检查的就越多。
这可能需要一些额外的工作，但总的来说，从长远来看它是值得的，并且可以实现更彻底的检查和更精确的工具支持。
在可能的情况下，新的代码库应该始终开启这些严格度检查。
:::

:::block
[en]
TypeScript has several type-checking strictness flags that can be turned on or off, and all of our examples will be written with all of them enabled unless otherwise stated.
The [`strict`](/tsconfig#strict) flag in the CLI, or `"strict": true` in a [`tsconfig.json`](https://www.typescriptlang.org/docs/handbook/tsconfig-json.html) toggles them all on simultaneously, but we can opt out of them individually.
The two biggest ones you should know about are [`noImplicitAny`](/tsconfig#noImplicitAny) and [`strictNullChecks`](/tsconfig#strictNullChecks).
[zh]
TypeScript 有几个可以开启或关闭的类型检查严格度标志，除非另有说明，我们所有的示例都将在开启所有标志的情况下编写。
CLI 中的 [`strict`](/tsconfig#strict) 标志，或者 [`tsconfig.json`](https://www.typescriptlang.org/docs/handbook/tsconfig-json.html) 中的 `"strict": true` 会同时开启所有这些标志，但我们可以单独关闭它们。
你需要了解的两个最重要的标志是 [`noImplicitAny`](/tsconfig#noImplicitAny) 和 [`strictNullChecks`](/tsconfig#strictNullChecks)。
:::

:::block
[en]
## `noImplicitAny`
[zh]
## `noImplicitAny`
:::

:::block
[en]
Recall that in some places, TypeScript doesn't try to infer types for us and instead falls back to the most lenient type: `any`.
This isn't the worst thing that can happen - after all, falling back to `any` is just the plain JavaScript experience anyway.
[zh]
回想一下，在某些地方，TypeScript 不会尝试为我们推断类型，而是退回到最宽松的类型：`any`。
这并不是可能发生的最坏情况——毕竟，退回到 `any` 无论如何都只是普通的 JavaScript 体验。
:::

:::block
[en]
However, using `any` often defeats the purpose of using TypeScript in the first place.
The more typed your program is, the more validation and tooling you'll get, meaning you'll run into fewer bugs as you code.
Turning on the [`noImplicitAny`](/tsconfig#noImplicitAny) flag will issue an error on any variables whose type is implicitly inferred as `any`.
[zh]
然而，使用 `any` 通常在一开始就违背了使用 TypeScript 的初衷。
你的程序类型定义得越完善，你获得的验证和工具支持就越多，这意味着你在编写代码时遇到的 bug 就会越少。
开启 [`noImplicitAny`](/tsconfig#noImplicitAny) 标志将在任何类型被隐式推断为 `any` 的变量上引发错误。
:::

:::block
[en]
## `strictNullChecks`
[zh]
## `strictNullChecks`
:::

:::block
[en]
By default, values like `null` and `undefined` are assignable to any other type.
This can make writing some code easier, but forgetting to handle `null` and `undefined` is the cause of countless bugs in the world - some consider it a [billion dollar mistake](https://www.youtube.com/watch?v=ybrQvs4x0Ps)!
The [`strictNullChecks`](/tsconfig#strictNullChecks) flag makes handling `null` and `undefined` more explicit, and _spares_ us from worrying about whether we _forgot_ to handle `null` and `undefined`.
[zh]
默认情况下，像 `null` 和 `undefined` 这样的值可以分配给任何其他类型。
这可以使编写某些代码更容易，但忘记处理 `null` 和 `undefined` 是世界上无数 bug 的根源——有些人认为这是 [十亿美元的错误](https://www.youtube.com/watch?v=ybrQvs4x0Ps)！
[`strictNullChecks`](/tsconfig#strictNullChecks) 标志使处理 `null` 和 `undefined` 更加显式，并 _免除_ 了我们担心是否 _忘记_ 了处理 `null` 和 `undefined`。
:::
