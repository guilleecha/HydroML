from django.core.management.base import BaseCommand
from experiments.models import MLExperiment
import mlflow
import mlflow.sklearn
from mlflow.entities import ViewType


class Command(BaseCommand):
    help = 'Display MLflow experiment tracking information'

    def add_arguments(self, parser):
        parser.add_argument(
            '--experiment-id',
            type=int,
            help='Django experiment ID to show MLflow info for',
        )

    def handle(self, *args, **options):
        try:
            # Set MLflow tracking URI
            mlflow.set_tracking_uri("http://mlflow:5000")
            
            experiment_id = options.get('experiment_id')
            
            if experiment_id:
                # Show specific experiment
                try:
                    experiment = MLExperiment.objects.get(id=experiment_id)
                    self.show_experiment_info(experiment)
                except MLExperiment.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'Experiment {experiment_id} not found')
                    )
            else:
                # Show all experiments
                self.show_all_experiments()
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error connecting to MLflow: {e}')
            )

    def show_experiment_info(self, experiment):
        """Show detailed info for a specific experiment"""
        self.stdout.write(
            self.style.SUCCESS(f'\n=== Experiment {experiment.id}: {experiment.name} ===')
        )
        
        self.stdout.write(f'Status: {experiment.status}')
        self.stdout.write(f'Model: {experiment.model_name}')
        self.stdout.write(f'Target Column: {experiment.target_column}')
        
        if experiment.mlflow_run_id:
            self.stdout.write(f'MLflow Run ID: {experiment.mlflow_run_id}')
            
            try:
                # Get MLflow run info
                run = mlflow.get_run(experiment.mlflow_run_id)
                
                self.stdout.write(f'\n--- MLflow Run Info ---')
                self.stdout.write(f'Status: {run.info.status}')
                self.stdout.write(f'Start Time: {run.info.start_time}')
                self.stdout.write(f'End Time: {run.info.end_time}')
                
                # Show parameters
                if run.data.params:
                    self.stdout.write(f'\n--- Parameters ---')
                    for key, value in run.data.params.items():
                        self.stdout.write(f'{key}: {value}')
                
                # Show metrics
                if run.data.metrics:
                    self.stdout.write(f'\n--- Metrics ---')
                    for key, value in run.data.metrics.items():
                        self.stdout.write(f'{key}: {value:.4f}')
                
                # Show artifacts
                artifacts = mlflow.list_artifacts(experiment.mlflow_run_id)
                if artifacts:
                    self.stdout.write(f'\n--- Artifacts ---')
                    for artifact in artifacts:
                        self.stdout.write(f'- {artifact.path}')
                        
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Could not retrieve MLflow run: {e}')
                )
        else:
            self.stdout.write('No MLflow run ID associated')

    def show_all_experiments(self):
        """Show summary of all experiments with MLflow integration"""
        self.stdout.write(
            self.style.SUCCESS('\n=== HydroML Experiments with MLflow Tracking ===')
        )
        
        experiments = MLExperiment.objects.all().order_by('-created_at')
        
        if not experiments:
            self.stdout.write('No experiments found')
            return
        
        self.stdout.write(f'{"ID":<5} {"Name":<20} {"Status":<12} {"Model":<20} {"MLflow Run":<20}')
        self.stdout.write('-' * 80)
        
        for exp in experiments:
            mlflow_status = exp.mlflow_run_id[:16] + '...' if exp.mlflow_run_id else 'No Run ID'
            self.stdout.write(
                f'{exp.id:<5} {exp.name[:19]:<20} {exp.status:<12} {exp.model_name[:19]:<20} {mlflow_status:<20}'
            )
        
        # Show MLflow experiments
        try:
            self.stdout.write(f'\n=== MLflow Experiments ===')
            mlflow_experiments = mlflow.search_experiments()
            
            for mlflow_exp in mlflow_experiments:
                self.stdout.write(f'- {mlflow_exp.name} (ID: {mlflow_exp.experiment_id})')
                
                # Count runs in this experiment
                runs = mlflow.search_runs(
                    experiment_ids=[mlflow_exp.experiment_id],
                    run_view_type=ViewType.ALL
                )
                self.stdout.write(f'  Runs: {len(runs)}')
                
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Could not retrieve MLflow experiments: {e}')
            )
