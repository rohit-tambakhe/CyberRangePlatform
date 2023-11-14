from kubernetes import client, config, watch
import requests
import json
import logging
import sys
import threading

# Load Kubernetes configuration from default location
config.load_incluster_config()

# Create Kubernetes API client
api = client.AutoscalingV2Api()

slack_url = "https://hooks.slack.com/services/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"

# Set up Slack webhook URL and channels
slack_channels_by_namespace = {
    "default": "#keda-hpa-alerts"
}

# List of HPA names to watch
hpa_names = ["garuda-app-stage-green-keda-hpa", "garuda-app-prod-keda-hpa", "claim-service-prod-keda-hpa"]
namespaces = ["transformer", "misool"]

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

def watch_hpas_in_namespace(namespace):
    while True:
        logging.info(f"Watching for HPAs in namespace '{namespace}'")
        for hpa_event in watch.Watch().stream(api.list_namespaced_horizontal_pod_autoscaler, namespace):
            hpa_name = hpa_event['object'].metadata.name
            # Check if the HPA is in the list of selected names and was triggered due to external metrics
            if hpa_name in hpa_names and hpa_event['object'].status.current_metrics:
                for metric in hpa_event['object'].status.current_metrics:
                    if metric.type == "External":
                        # Check if the HPA is scaling up or down
                        desired_replicas = hpa_event['object'].status.desired_replicas
                        old_replicas = hpa_event['object'].status.current_replicas
                        if desired_replicas != old_replicas:
                            scaling_direction = "up" if desired_replicas > old_replicas else "down"
                        # Send Slack alert with current average_value of external metric
                            average_value = metric.external.current.average_value
                            if average_value.endswith("m"):
                                average_value = float(average_value[:-1]) / 1000  
                            message = hpa_event['object'].status.conditions[-2].message
                            logging.info(f"Watching for HPAs in namespace '{message}'")
                            metric_name=""
                            logging.info(f"average_value: {average_value}")
                            logging.info(f"metric-name '{metric_name}'")
                            if scaling_direction == "up" and "external metric" in message and int(average_value) > 500:
                                metric_name=metric.external.metric.name   
                                logging.info(f"metric-name '{metric_name}'")                        
                                message = (
                                    f"*HORIZONTAL POD AUTOSCALER EVENT*\n"
                                    f"- HPA name: {hpa_name}\n"
                                    f"- Namespace: {namespace}\n"
                                    f"- Scaling direction: {scaling_direction}\n"
                                    f"- Desired replicas: {desired_replicas}\n"
                                    f"- Old replicas: {old_replicas}\n"
                                    f"- External metric name: {metric.external.metric.name}\n"
                                    f"- Current average value: {average_value}\n"
                                )
                                logging.info(message)
                                channel = slack_channels_by_namespace.get(namespace, slack_channels_by_namespace["default"])
                                payload = {
                                    "channel": channel,
                                    "text": message
                                }
                                headers = {
                                    "Content-type": "application/json"
                                    }
                                try:
                                    response = requests.post(slack_url, data=json.dumps(payload), headers=headers)
                                    response.raise_for_status()
                                    logging.info("Slack alert sent successfully")
                                except requests.exceptions.HTTPError as e:
                                    logging.error(f"Error sending Slack message: {e}")
                            logging.info(f"metric-name '{metric_name}'")
                            if  scaling_direction == "down":
                                logging.info(f"metric-name '{metric_name}'")
                                message = (
                                    f"*HORIZONTAL POD AUTOSCALER EVENT*\n"
                                    f"- HPA name: {hpa_name}\n"
                                    f"- Namespace: {namespace}\n"
                                    f"- Scaling direction: {scaling_direction}\n"
                                    f"- Desired replicas: {desired_replicas}\n"
                                    f"- Old replicas: {old_replicas}\n"
                                    f"- External metric name: {metric.external.metric.name}\n"
                                    f"- Current average value: {average_value}\n"
                                    f"- All metrics below threshold\n"
                                )
                                logging.info(message)
                                channel = slack_channels_by_namespace.get(namespace, slack_channels_by_namespace["default"])
                                payload = {
                                    "channel": channel,
                                    "text": message
                                }
                                headers = {
                                    "Content-type": "application/json"
                        
                                }
                                try:
                                    response = requests.post(slack_url, data=json.dumps(payload), headers=headers)
                                    response.raise_for_status()
                                    logging.info("Slack alert sent successfully")
                                except requests.exceptions.HTTPError as e:
                                      logging.error(f"Error sending Slack message: {e}")
                                metric_name = ""
threads = []
for namespace in namespaces:
    t = threading.Thread(target=watch_hpas_in_namespace, args=(namespace,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
