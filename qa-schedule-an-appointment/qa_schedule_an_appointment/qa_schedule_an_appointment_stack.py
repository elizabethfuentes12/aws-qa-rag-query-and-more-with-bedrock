from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    aws_dynamodb as ddb,
    RemovalPolicy,
    aws_iam as iam,
)
from constructs import Construct
from lambdas import Lambdas
from databases import Tables
from s3_cloudfront import S3Deploy

REMOVAL_POLICY = RemovalPolicy.DESTROY
TABLE_CONFIG = dict (removal_policy=REMOVAL_POLICY, billing_mode= ddb.BillingMode.PAY_PER_REQUEST)

ENV_KEY_NAME = "date"
env_key_sec_global = "phone_number"
bedrock_model_id = "anthropic.claude-instant-v1"
bedrock_embedding_model_id = 'amazon.titan-embed-text-v1'

class QaScheduleAnAppointmentStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        stk = Stack.of(self)
        account_id = stk.account
        region_name = self.region

        #Create Amazon S3 Bucke and upload the data into the folder vectordb
        s3_deploy = S3Deploy(self, "spa-data", "vectordb","vectordb")

        #Create Amazon DynamoDB Tables
        Tbl = Tables(self, 'Tbl')

        Tbl.spa_table.add_global_secondary_index(index_name = 'phoneindex', 
                                                            partition_key = ddb.Attribute(name=env_key_sec_global,type=ddb.AttributeType.STRING), 
                                                            projection_type=ddb.ProjectionType.KEYS_ONLY)
        #Create Amazon Lamda Functions 

        Fn  = Lambdas(self,'Fn')

        Fn.agent.add_environment(key='TABLE_NAME', value= Tbl.spa_table.table_name)
        Fn.agent.add_environment(key='TABLE_SESSION', value= Tbl.session_table.table_name)

        Fn.agent.add_environment(key='MODEL_ID', value= bedrock_model_id)
        Fn.agent.add_environment(key='LAMBDA_QUERY_NAME', value= Fn.dynamodb_query.function_name)
        Fn.agent.add_environment(key='LAMBDA_PUT_NAME', value= Fn.dynamodb_put_item.function_name)
        Fn.agent.add_environment(key='BUCKET_NAME', value= s3_deploy.bucket.bucket_name)
        Fn.agent.add_environment(key='EMBEDDING_MODEL', value= bedrock_embedding_model_id)

        s3_deploy.bucket.grant_read(Fn.agent)
        
        Tbl.spa_table.grant_full_access(Fn.agent)
        Tbl.session_table.grant_full_access(Fn.agent)

        Fn.agent.add_to_role_policy(iam.PolicyStatement(actions=["lambda:InvokeFunction"], resources=[Fn.dynamodb_query.function_arn]))
        Fn.agent.add_to_role_policy(iam.PolicyStatement(actions=["lambda:InvokeFunction"], resources=[Fn.dynamodb_put_item.function_arn]))
        Fn.agent.add_to_role_policy(iam.PolicyStatement(actions=["bedrock:*"], resources=['*']))

        Tbl.spa_table.grant_full_access(Fn.dynamodb_put_item)
        Tbl.spa_table.grant_full_access(Fn.dynamodb_query)

        Fn.dynamodb_put_item.add_environment(key='TABLE_NAME', value= Tbl.spa_table.table_name)
        Fn.dynamodb_put_item.add_environment(key='TABLE_NAME', value= Tbl.spa_table.table_name)

        Fn.dynamodb_query.add_environment(key='ENV_KEY_NAME', value= env_key_sec_global)
        
