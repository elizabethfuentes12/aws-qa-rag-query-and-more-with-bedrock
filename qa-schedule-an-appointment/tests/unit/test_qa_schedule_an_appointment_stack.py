import aws_cdk as core
import aws_cdk.assertions as assertions

from qa_schedule_an_appointment.qa_schedule_an_appointment_stack import QaScheduleAnAppointmentStack

# example tests. To run these tests, uncomment this file along with the example
# resource in qa_schedule_an_appointment/qa_schedule_an_appointment_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = QaScheduleAnAppointmentStack(app, "qa-schedule-an-appointment")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
