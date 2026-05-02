import argparse

import iamcli_common
import iamfunction


def main():
    parser = argparse.ArgumentParser()
    iamcli_common.add_account_args(parser)
    parser.add_argument('--policy-name')
    parser.add_argument('--policy-json')
    parser.add_argument('--policy-file')
    args = parser.parse_args()

    def process_account(account, iam):
        if args.policy_name:
            targets = [{'name': args.policy_name}]
        else:
            targets = iamcli_common.get_config_list(account, 'create_policies')

        if len(targets) == 0:
            print('作成対象ポリシーなし')
            return

        for target in targets:
            if isinstance(target, str):
                target = {'name': target}

            policy_name = target['name']

            try:
                policy_document = iamcli_common.load_policy_document(
                    account,
                    args,
                    target,
                )
            except ValueError as e:
                print('入力エラー: ' + str(e))
                return

            result = iamfunction.create_policy(policy_name, policy_document, iam)
            print(result['Note'])
            if result['Created']:
                print('PolicyArn: ' + result['PolicyArn'])

    if not args.config and not args.policy_name:
        print('入力エラー: configなしの場合、--policy-name を指定してください')
        return

    iamcli_common.run_for_accounts(args, process_account)


if __name__ == '__main__':
    main()
