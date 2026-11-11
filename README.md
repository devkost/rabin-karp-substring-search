# Поиск подстрок

Консольная программа ищет одну или несколько подстрок алгоритмом Рабина—Карпа.

## Запуск

Поиск в тексте:

```bash
python3 main.py --text "ababbababa" --patterns aba bba
```

Поиск в файле:

```bash
python3 main.py --file input.txt --patterns aba
```

Дополнительные параметры:

- `--case-sensitive` — учитывать регистр;
- `--method first` или `--method last` — искать с начала или с конца;
- `--count 2` — вывести не более двух совпадений всего (если подстрок несколько);
- `--no-color` — отключить цветную подсветку.

Пример со всеми параметрами:

```bash
python3 main.py --file input.txt --patterns aba bba --case-sensitive --method last --count 2
```

## Тесты

```bash
python3 -m unittest -v test_search.py
```
