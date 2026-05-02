# YAML の書き方マニュアル

この資料は、`config.yaml` を書くために必要な YAML の基本を説明します。
このプロジェクト専用の設定例は `CONFIG_WRITING_GUIDE.md` を見ます。

## YAMLとは

YAMLは、設定ファイルを書くためによく使われる形式です。

Pythonでは次のように読み込んで使います。

```python
import yaml

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
```

## 基本ルール

YAMLで一番大事なのはインデントです。

```yaml
accounts:
  - name: account-a
    account_id: '111111111111'
```

`accounts:` の下にあるものは、半角スペースで右にずらします。

## スペースを使う

YAMLでは、インデントにタブを使わず、半角スペースを使います。

良い例:

```yaml
accounts:
  - name: account-a
```

悪い例:

```yaml
accounts:
	- name: account-a
```

見た目は似ていますが、タブが入るとエラーになることがあります。

## key と value

基本は `key: value` の形です。

```yaml
name: account-a
account_id: '111111111111'
access_key: test
secret_key: test
```

Pythonで読むと、辞書になります。

```python
{
    'name': 'account-a',
    'account_id': '111111111111',
    'access_key': 'test',
    'secret_key': 'test',
}
```

## リスト

複数の値を書く時は `-` を使います。

```yaml
create_users:
  - user-a
  - user-b
  - user-c
```

Pythonで読むと、リストになります。

```python
['user-a', 'user-b', 'user-c']
```

## 辞書のリスト

アカウントのように、複数の項目を持つものを並べる時は、辞書のリストにします。

```yaml
accounts:
  - name: account-a
    account_id: '111111111111'
    access_key: test
    secret_key: test

  - name: account-b
    account_id: '222222222222'
    access_key: test
    secret_key: test
```

Pythonで読むと、こういう形です。

```python
{
    'accounts': [
        {
            'name': 'account-a',
            'account_id': '111111111111',
            'access_key': 'test',
            'secret_key': 'test',
        },
        {
            'name': 'account-b',
            'account_id': '222222222222',
            'access_key': 'test',
            'secret_key': 'test',
        },
    ]
}
```

## 名前付きの辞書

ポリシーのように、名前を付けて管理したい時は辞書にします。

```yaml
policies:
  policy-a:
    arn: arn:aws:iam::111111111111:policy/policy-a
    file: ../policy-a.json

  policy-b:
    arn: arn:aws:iam::111111111111:policy/policy-b
    file: ../policy-b.json
```

この形は、`policy-a` という名前で設定を取り出しやすいです。

## 文字列のクォート

文字列は、基本的にはクォートなしでも書けます。

```yaml
name: account-a
```

ただし、数字だけのIDは文字列として扱いたいので、クォートするのがおすすめです。

```yaml
account_id: '111111111111'
```

ARNは `:` が多いですが、通常はそのままでも読めます。

```yaml
arn: arn:aws:iam::111111111111:policy/policy-a
```

迷ったらシングルクォートで囲んでOKです。

```yaml
arn: 'arn:aws:iam::111111111111:policy/policy-a'
```

## 空のリスト

対象がない時は、空リストを書けます。

```yaml
delete_users: []
delete_groups: []
delete_policies: []
```

複数行で空にする場合は、何も書かないより `[]` の方が分かりやすいです。

## コメント

`#` から右側はコメントです。

```yaml
account_id: '111111111111'  # moto用アカウントID
```

## よくあるミス

### インデントがずれている

悪い例:

```yaml
accounts:
  - name: account-a
  account_id: '111111111111'
```

`account_id` は `name` と同じアカウントの項目なので、同じ位置に揃えます。

良い例:

```yaml
accounts:
  - name: account-a
    account_id: '111111111111'
```

### `-` を忘れる

悪い例:

```yaml
create_users:
  user-a
  user-b
```

良い例:

```yaml
create_users:
  - user-a
  - user-b
```

### `:` の後ろにスペースがない

悪い例:

```yaml
name:account-a
```

良い例:

```yaml
name: account-a
```

### リストと辞書を混ぜてしまう

このプロジェクトでは、ユーザーやグループはリストで書きます。

```yaml
create_users:
  - user-a
  - user-b
```

ポリシー定義は、名前付き辞書で書きます。

```yaml
policies:
  policy-a:
    arn: ...
    file: ...
```

## このプロジェクトでよく使う形

### ユーザー一覧

```yaml
create_users:
  - user-a
  - user-b
```

### グループ一覧

```yaml
create_groups:
  - group-a
  - group-b
```

### ポリシー定義

```yaml
policies:
  aa:
    arn: arn:aws:iam::111111111111:policy/aa
    file: ../A.json
```

### ポリシーの関連付け

```yaml
attach_user_policies:
  - user: user-a
    policy: aa
```

この `policy: aa` は、`policies.aa` を参照するための名前です。

## 最小の config.yaml 例

```yaml
accounts:
  - name: account-a
    account_id: '111111111111'
    access_key: test
    secret_key: test
```

## 複数アカウントの例

```yaml
accounts:
  - name: account-a
    account_id: '111111111111'
    access_key: test
    secret_key: test

  - name: account-b
    account_id: '222222222222'
    access_key: test
    secret_key: test
```

## 確認方法

PythonでYAMLが読めるか確認できます。

```bash
python3 -c "import yaml; print(yaml.safe_load(open('config.yaml')))"
```

エラーが出なければ、YAMLとしては読めています。

## 読み分け

YAMLの基本:

```text
YAML_GUIDE.md
```

このプロジェクト用のconfig例:

```text
CONFIG_WRITING_GUIDE.md
```

コマンドの使い方:

```text
COMMAND_MANUAL.md
```
