import argparse

import iamcli_common
import iamfunction


def main():
    parser = argparse.ArgumentParser()
    iamcli_common.add_account_args(parser)
    parser.add_argument('--policy-arn')
    parser.add_argument('--policy-name')
    args = parser.parse_args()

    def process_account(account, iam):
        if args.policy_arn or args.policy_name:
            targets = [{'policy_name': args.policy_name}]
        else:
            targets = iamcli_common.get_config_list(account, 'delete_policies')

        if len(targets) == 0:
            print('削除対象ポリシーなし')
            return

        for target in targets:
            if isinstance(target, str):
                target = {'policy_name': target}

            try:
                policy_arn = iamcli_common.get_policy_arn(
                    account,
                    cli_policy_arn=args.policy_arn,
                    policy_name=target.get('policy_name') or target.get('name'),
                    config_value=target,
                )
            except ValueError as e:
                print('入力エラー: ' + str(e))
                return

            result = iamfunction.delete_policy(policy_arn, iam)
            print(result['Note'])
            if result['Deleted']:
                detached = result['Detached']
                if len(detached['Users']) > 0:
                    print('detach users: ' + ', '.join(detached['Users']))
                if len(detached['Groups']) > 0:
                    print('detach groups: ' + ', '.join(detached['Groups']))
                if len(detached['Roles']) > 0:
                    print('detach roles: ' + ', '.join(detached['Roles']))

    if not args.config and not args.policy_arn:
        print('入力エラー: configなしの場合、--policy-arn を指定してください')
        return

    iamcli_common.run_for_accounts(args, process_account)


if __name__ == '__main__':
    main()
