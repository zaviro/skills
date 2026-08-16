# Markdown Syntax Reference

## Headers
```markdown
# H1
## H2
### H3
```

## Emphasis
```markdown
*italic* or _italic_
**bold** or __bold__
***bold italic***
~~strikethrough~~
==highlight==
```

## Lists
```markdown
- Unordered item
  - Nested item

1. Ordered item
2. Second item

- [ ] Task unchecked
- [x] Task checked
```

## Links & Images
```markdown
[Link text](https://url.com)
[[Internal link]]
[[Link|Display text]]
![[image.png]]
![Alt text](image-url.png)
```

## Code
````markdown
Inline `code`

```python
def hello():
    print("Hello")
```
````

## Quotes & Callouts
```markdown
> Blockquote

> [!note]
> This is a callout

> [!warning]
> Warning callout

> [!tip]
> Tip callout
```

## Tables
```markdown
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
```

## Math (LaTeX)
```markdown
Inline: $E = mc^2$

Block:
$$
\sum_{i=1}^{n} x_i
$$
```

## Footnotes
```markdown
Here is a footnote[^1].

[^1]: Footnote content.
```
