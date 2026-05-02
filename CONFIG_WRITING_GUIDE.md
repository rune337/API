# config.yaml の書き方

この資料は、`config.yaml` にユーザー、グループ、ポリシーを複数書く方法を説明します。
YAMLの基本文法は `YAML_GUIDE.md` を見ます。

## 基本

`config.yaml` は、アカウントごとに設定を書きます。

```yaml
accounts:
  - name: account-a
    account_id: '111111111111'
    access_key: test
    secret_key: test
```

`accounts:` の下に `-` でアカウントを並べます。

## ユーザーを複数書く

ユーザーを複数作る場合は、`create_users` にリストで書きます。

```yaml
accounts:
  - name: account-a
    account_id: '111111111111'
    access_key: test
    secret_key: test
    create_users:
      - user-a
      - user-b
      - user-c
```

削除対象ユーザーは `delete_users` に書きます。

```yaml
delete_users:
  - old-user-a
  - old-user-b
```

実行:

```bash
python3 create_user.py --config ./config.yaml --use-account-id
python3 delete_user.py --config ./config.yaml --use-account-id
```

## グループを複数書く

グループを複数作る場合は、`create_groups` にリストで書きます。

```yaml
create_groups:
  - group-a
  - group-b
  - group-c
```

削除対象グループは `delete_groups` に書きます。

```yaml
delete_groups:
  - old-group-a
  - old-group-b
```

実行:

```bash
python3 create_group.py --config ./config.yaml --use-account-id
python3 delete_group.py --config ./config.yaml --use-account-id
```

## ポリシー定義を複数書く

ポリシーは `policies` に名前を付けて書くのがおすすめです。

```yaml
policies:
  policy-a:
    arn: arn:aws:iam::111111111111:policy/policy-a
    file: ../policy-a.json

  policy-b:
    arn: arn:aws:iam::111111111111:policy/policy-b
    file: ../policy-b.json

  policy-c:
    arn: arn:aws:iam::111111111111:policy/policy-c
    file: ../policy-c.json
```

この `policy-a` や `policy-b` は、あとで `policy: policy-a` のように参照できます。

## ポリシーを複数作る

作成するポリシーは `create_policies` に書きます。

```yaml
create_policies:
  - name: policy-a
    file: ../policy-a.json

  - name: policy-b
    file: ../policy-b.json
```

実行:

```bash
python3 create_policy.py --config ./config.yaml --use-account-id
```

`name` は作成するポリシー名です。
`file` は読み込むポリシーJSONです。

## ポリシーを複数更新する

更新対象は `update_policies` に書きます。

```yaml
update_policies:
  - policy_name: policy-a
    file: ../policy-a-new.json

  - policy_name: policy-b
    file: ../policy-b-new.json
```

実行:

```bash
python3 update_policy.py --config ./config.yaml --use-account-id
```

`policy_name: policy-a` は、同じアカウント内の `policies.policy-a.arn` を見に行きます。

## ポリシーを複数削除する

削除対象は `delete_policies` に書きます。

```yaml
delete_policies:
  - policy_name: policy-a
  - policy_name: policy-b
```

実行:

```bash
python3 delete_policy.py --config ./config.yaml --use-account-id
```

## ユーザーにポリシーを複数追加する

ユーザーにポリシーを付ける場合は、`attach_user_policies` に書きます。

```yaml
attach_user_policies:
  - user: user-a
    policy: policy-a

  - user: user-b
    policy: policy-b

  - user: user-c
    policy: policy-a
```

実行:

```bash
python3 attach_user_policy.py --config ./config.yaml --use-account-id
```

`policy: policy-a` は、`policies.policy-a` を参照します。

## ユーザーからポリシーを複数削除する

ユーザーから外す場合は、`detach_user_policies` に書きます。

```yaml
detach_user_policies:
  - user: user-a
    policy: policy-a

  - user: user-b
    policy: policy-b
```

実行:

```bash
python3 detach_user_policy.py --config ./config.yaml --use-account-id
```

## グループにポリシーを複数追加する

グループにポリシーを付ける場合は、`attach_group_policies` に書きます。

```yaml
attach_group_policies:
  - group: group-a
    policy: policy-a

  - group: group-b
    policy: policy-b
```

実行:

```bash
python3 attach_group_policy.py --config ./config.yaml --use-account-id
```

## グループからポリシーを複数削除する

グループから外す場合は、`detach_group_policies` に書きます。

```yaml
detach_group_policies:
  - group: group-a
    policy: policy-a

  - group: group-b
    policy: policy-b
```

実行:

```bash
python3 detach_group_policy.py --config ./config.yaml --use-account-id
```

## 全部入りの例

```yaml
accounts:
  - name: account-a
    account_id: '111111111111'
    access_key: test
    secret_key: test

    create_users:
      - user-a
      - user-b
      - user-c

    delete_users:
      - old-user-a
      - old-user-b

    create_groups:
      - group-a
      - group-b

    delete_groups:
      - old-group-a
      - old-group-b

    policies:
      policy-a:
        arn: arn:aws:iam::111111111111:policy/policy-a
        file: ../policy-a.json

      policy-b:
        arn: arn:aws:iam::111111111111:policy/policy-b
        file: ../policy-b.json

      policy-c:
        arn: arn:aws:iam::111111111111:policy/policy-c
        file: ../policy-c.json

    create_policies:
      - name: policy-a
        file: ../policy-a.json

      - name: policy-b
        file: ../policy-b.json

    update_policies:
      - policy_name: policy-a
        file: ../policy-a-new.json

      - policy_name: policy-b
        file: ../policy-b-new.json

    delete_policies:
      - policy_name: policy-c

    attach_user_policies:
      - user: user-a
        policy: policy-a

      - user: user-b
        policy: policy-b

    detach_user_policies:
      - user: user-a
        policy: policy-a

    attach_group_policies:
      - group: group-a
        policy: policy-a

      - group: group-b
        policy: policy-b

    detach_group_policies:
      - group: group-a
        policy: policy-a
```

## 書き方のポイント

複数の値は、基本的に `-` で並べます。

```yaml
create_users:
  - user-a
  - user-b
```

ポリシー定義は、名前付きでまとめます。

```yaml
policies:
  policy-a:
    arn: ...
    file: ...
```

関連付けでは、ポリシー名を参照します。

```yaml
attach_user_policies:
  - user: user-a
    policy: policy-a
```

この形にすると、ARNやJSONファイルの場所を何度も書かずに済みます。
