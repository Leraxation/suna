"""
Data Processing and Analytics Tool for Suna AI
Provides advanced data processing, transformation, and analytics capabilities
Integrates with existing Suna AI data providers and extends functionality
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import asyncio
import io
import csv
from collections import defaultdict

from agentpress.tool import Tool, ToolResult, openapi_schema, xml_schema
from services.llm import make_llm_api_call
from utils.logger import logger
from utils.config import config

class DataProcessingTool(Tool):
    """Advanced data processing and analytics tool."""

    def __init__(self):
        super().__init__()
        self.processing_cache = {}
        self.data_pipelines = {}
        
    @openapi_schema({
        "type": "function",
        "function": {
            "name": "process_dataset",
            "description": "Process and transform datasets with advanced analytics and cleaning operations",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "Dataset to process (array of objects)"
                    },
                    "operations": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Processing operations to perform",
                        "default": ["clean", "analyze", "summarize"]
                    },
                    "output_format": {
                        "type": "string",
                        "description": "Output format (json, csv, summary)",
                        "default": "json"
                    },
                    "include_statistics": {
                        "type": "boolean",
                        "description": "Include statistical analysis",
                        "default": True
                    }
                },
                "required": ["data"]
            }
        }
    })
    @xml_schema(
        tag_name="process-dataset",
        mappings=[
            {"param_name": "data", "node_type": "content", "path": "."},
            {"param_name": "operations", "node_type": "attribute", "path": "operations"},
            {"param_name": "output_format", "node_type": "attribute", "path": "output_format"},
            {"param_name": "include_statistics", "node_type": "attribute", "path": "include_statistics"}
        ],
        example='''
        <function_calls>
        <invoke name="process_dataset">
        <parameter name="data">[{"name": "John", "age": 30, "salary": 50000}, {"name": "Jane", "age": 25, "salary": 60000}]</parameter>
        <parameter name="operations">["clean", "analyze", "correlate"]</parameter>
        <parameter name="output_format">json</parameter>
        <parameter name="include_statistics">true</parameter>
        </invoke>
        </function_calls>
        '''
    )
    async def process_dataset(
        self, 
        data: List[Dict[str, Any]], 
        operations: List[str] = None,
        output_format: str = "json",
        include_statistics: bool = True
    ) -> ToolResult:
        """Process and analyze datasets with advanced operations."""
        try:
            if operations is None:
                operations = ["clean", "analyze", "summarize"]
            
            if not data:
                return self.fail_response("No data provided for processing")
            
            # Convert to DataFrame for easier processing
            try:
                df = pd.DataFrame(data)
            except Exception as e:
                return self.fail_response(f"Failed to convert data to DataFrame: {str(e)}")
            
            results = {
                "original_data_info": {
                    "rows": len(df),
                    "columns": len(df.columns),
                    "column_names": list(df.columns),
                    "data_types": df.dtypes.to_dict()
                },
                "processing_operations": operations,
                "processed_data": {},
                "statistics": {},
                "insights": []
            }
            
            # Perform requested operations
            for operation in operations:
                if operation == "clean":
                    cleaned_data = await self._clean_data(df)
                    results["processed_data"]["cleaned"] = cleaned_data
                    
                elif operation == "analyze":
                    analysis = await self._analyze_data(df)
                    results["processed_data"]["analysis"] = analysis
                    
                elif operation == "summarize":
                    summary = await self._summarize_data(df)
                    results["processed_data"]["summary"] = summary
                    
                elif operation == "correlate":
                    correlations = await self._calculate_correlations(df)
                    results["processed_data"]["correlations"] = correlations
                    
                elif operation == "outliers":
                    outliers = await self._detect_outliers(df)
                    results["processed_data"]["outliers"] = outliers
                    
                elif operation == "normalize":
                    normalized = await self._normalize_data(df)
                    results["processed_data"]["normalized"] = normalized
            
            # Include statistics if requested
            if include_statistics:
                results["statistics"] = {
                    "descriptive_stats": df.describe().to_dict() if len(df.select_dtypes(include=[np.number]).columns) > 0 else {},
                    "missing_values": df.isnull().sum().to_dict(),
                    "unique_values": {col: df[col].nunique() for col in df.columns},
                    "data_quality_score": self._calculate_data_quality_score(df)
                }
            
            # Generate AI-powered insights
            insights = await self._generate_insights(df, results)
            results["insights"] = insights
            
            # Format output
            if output_format == "csv":
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False)
                results["csv_output"] = csv_buffer.getvalue()
            elif output_format == "summary":
                results = {
                    "summary": results["processed_data"].get("summary", {}),
                    "key_insights": results["insights"][:3],
                    "data_quality": results["statistics"].get("data_quality_score", "N/A")
                }
            
            # Cache results
            cache_key = f"dataset_{hash(str(data))}"
            self.processing_cache[cache_key] = {
                "results": results,
                "timestamp": datetime.now().isoformat(),
                "operations": operations
            }
            
            return self.success_response({
                "data_processing_results": results,
                "cache_key": cache_key,
                "processing_timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Dataset processing failed: {str(e)}")
            return self.fail_response(f"Dataset processing failed: {str(e)}")

    async def _clean_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Clean the dataset by handling missing values, duplicates, etc."""
        cleaning_results = {
            "original_shape": df.shape,
            "operations_performed": [],
            "cleaned_data_preview": {}
        }
        
        # Handle missing values
        missing_before = df.isnull().sum().sum()
        if missing_before > 0:
            # Fill numeric columns with median, categorical with mode
            for col in df.columns:
                if df[col].dtype in ['int64', 'float64']:
                    df[col].fillna(df[col].median(), inplace=True)
                else:
                    df[col].fillna(df[col].mode().iloc[0] if not df[col].mode().empty else 'Unknown', inplace=True)
            cleaning_results["operations_performed"].append(f"Filled {missing_before} missing values")
        
        # Remove duplicates
        duplicates_before = df.duplicated().sum()
        if duplicates_before > 0:
            df.drop_duplicates(inplace=True)
            cleaning_results["operations_performed"].append(f"Removed {duplicates_before} duplicate rows")
        
        # Remove columns with all null values
        null_cols = df.columns[df.isnull().all()].tolist()
        if null_cols:
            df.drop(columns=null_cols, inplace=True)
            cleaning_results["operations_performed"].append(f"Removed columns with all null values: {null_cols}")
        
        cleaning_results["final_shape"] = df.shape
        cleaning_results["cleaned_data_preview"] = df.head(3).to_dict('records')
        
        return cleaning_results

    async def _analyze_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform comprehensive data analysis."""
        analysis = {
            "data_overview": {
                "shape": df.shape,
                "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB",
                "column_types": df.dtypes.value_counts().to_dict()
            },
            "numerical_analysis": {},
            "categorical_analysis": {},
            "patterns": []
        }
        
        # Numerical analysis
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            analysis["numerical_analysis"] = {
                "columns": list(numeric_cols),
                "statistics": df[numeric_cols].describe().to_dict(),
                "distributions": {col: {
                    "skewness": float(df[col].skew()),
                    "kurtosis": float(df[col].kurtosis())
                } for col in numeric_cols}
            }
        
        # Categorical analysis
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            analysis["categorical_analysis"] = {
                "columns": list(categorical_cols),
                "value_counts": {col: df[col].value_counts().head(5).to_dict() for col in categorical_cols},
                "cardinality": {col: df[col].nunique() for col in categorical_cols}
            }
        
        return analysis

    async def _summarize_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate a comprehensive data summary."""
        summary = {
            "dataset_overview": {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "data_types": df.dtypes.value_counts().to_dict(),
                "missing_data_percentage": (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            },
            "key_statistics": {},
            "data_quality_indicators": {}
        }
        
        # Key statistics for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            summary["key_statistics"]["numerical"] = {
                col: {
                    "mean": float(df[col].mean()),
                    "median": float(df[col].median()),
                    "std": float(df[col].std()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max())
                } for col in numeric_cols
            }
        
        # Data quality indicators
        summary["data_quality_indicators"] = {
            "completeness": (1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
            "uniqueness": (df.drop_duplicates().shape[0] / len(df)) * 100,
            "consistency": 100 - (df.dtypes.value_counts().get('object', 0) / len(df.columns)) * 20  # Simplified metric
        }
        
        return summary

    async def _calculate_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate correlations between numerical variables."""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if len(numeric_df.columns) < 2:
            return {"message": "Insufficient numerical columns for correlation analysis"}
        
        correlation_matrix = numeric_df.corr()
        
        # Find strong correlations (> 0.7 or < -0.7)
        strong_correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:
                    strong_correlations.append({
                        "variable_1": correlation_matrix.columns[i],
                        "variable_2": correlation_matrix.columns[j],
                        "correlation": float(corr_value),
                        "strength": "strong positive" if corr_value > 0.7 else "strong negative"
                    })
        
        return {
            "correlation_matrix": correlation_matrix.to_dict(),
            "strong_correlations": strong_correlations,
            "correlation_summary": {
                "highest_positive": float(correlation_matrix.max().max()),
                "lowest_negative": float(correlation_matrix.min().min()),
                "average_correlation": float(correlation_matrix.mean().mean())
            }
        }

    async def _detect_outliers(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect outliers in numerical columns using IQR method."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        outliers_info = {}
        
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
            
            outliers_info[col] = {
                "outlier_count": len(outliers),
                "outlier_percentage": (len(outliers) / len(df)) * 100,
                "bounds": {"lower": float(lower_bound), "upper": float(upper_bound)},
                "outlier_values": outliers[col].tolist()[:10]  # First 10 outliers
            }
        
        return outliers_info

    async def _normalize_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Normalize numerical data using min-max scaling."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        normalized_data = df.copy()
        
        normalization_info = {}
        
        for col in numeric_cols:
            min_val = df[col].min()
            max_val = df[col].max()
            
            if max_val != min_val:  # Avoid division by zero
                normalized_data[col] = (df[col] - min_val) / (max_val - min_val)
                normalization_info[col] = {
                    "original_range": {"min": float(min_val), "max": float(max_val)},
                    "normalized_range": {"min": 0.0, "max": 1.0}
                }
        
        return {
            "normalized_data": normalized_data.head(5).to_dict('records'),
            "normalization_info": normalization_info,
            "columns_normalized": list(numeric_cols)
        }

    def _calculate_data_quality_score(self, df: pd.DataFrame) -> float:
        """Calculate an overall data quality score."""
        # Completeness (no missing values)
        completeness = (1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        
        # Uniqueness (no duplicates)
        uniqueness = (df.drop_duplicates().shape[0] / len(df)) * 100
        
        # Consistency (reasonable data types)
        consistency = 100 - (df.dtypes.value_counts().get('object', 0) / len(df.columns)) * 20
        
        # Overall score (weighted average)
        quality_score = (completeness * 0.4 + uniqueness * 0.3 + consistency * 0.3)
        
        return round(quality_score, 2)

    async def _generate_insights(self, df: pd.DataFrame, results: Dict[str, Any]) -> List[str]:
        """Generate AI-powered insights about the dataset."""
        try:
            # Prepare data summary for AI analysis
            data_summary = {
                "shape": df.shape,
                "columns": list(df.columns),
                "data_types": df.dtypes.to_dict(),
                "sample_data": df.head(3).to_dict('records'),
                "statistics": results.get("statistics", {})
            }
            
            model_to_use = config.MODEL_TO_USE
            
            messages = [{
                "role": "user",
                "content": f"""
                Analyze this dataset and provide 5-7 key insights:
                
                Dataset Summary: {json.dumps(data_summary, indent=2, default=str)}
                
                Please provide insights about:
                1. Data quality and completeness
                2. Interesting patterns or trends
                3. Potential data issues or anomalies
                4. Recommendations for further analysis
                5. Business or research implications
                
                Return insights as a JSON array of strings.
                """
            }]
            
            response = await make_llm_api_call(
                messages=messages,
                model_name=model_to_use,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            insights_data = json.loads(response.choices[0].message.content)
            return insights_data.get("insights", ["No insights generated"])
            
        except Exception as e:
            logger.error(f"Insight generation failed: {str(e)}")
            return [f"Insight generation failed: {str(e)}"]

    @openapi_schema({
        "type": "function",
        "function": {
            "name": "create_data_pipeline",
            "description": "Create and manage data processing pipelines for automated data workflows",
            "parameters": {
                "type": "object",
                "properties": {
                    "pipeline_name": {
                        "type": "string",
                        "description": "Name for the data pipeline"
                    },
                    "data_source": {
                        "type": "string",
                        "description": "Data source configuration (api, file, database)"
                    },
                    "processing_steps": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of processing steps to include in pipeline"
                    },
                    "schedule": {
                        "type": "string",
                        "description": "Pipeline execution schedule (hourly, daily, weekly)",
                        "default": "manual"
                    }
                },
                "required": ["pipeline_name", "processing_steps"]
            }
        }
    })
    async def create_data_pipeline(
        self, 
        pipeline_name: str, 
        processing_steps: List[str],
        data_source: str = "manual",
        schedule: str = "manual"
    ) -> ToolResult:
        """Create a data processing pipeline."""
        try:
            pipeline_config = {
                "name": pipeline_name,
                "data_source": data_source,
                "processing_steps": processing_steps,
                "schedule": schedule,
                "created_at": datetime.now().isoformat(),
                "status": "created",
                "execution_history": []
            }
            
            # Store pipeline configuration
            self.data_pipelines[pipeline_name] = pipeline_config
            
            return self.success_response({
                "pipeline_created": pipeline_config,
                "pipeline_id": pipeline_name,
                "next_steps": [
                    "Use execute_data_pipeline to run the pipeline",
                    "Monitor pipeline performance with get_pipeline_status"
                ]
            })
            
        except Exception as e:
            logger.error(f"Pipeline creation failed: {str(e)}")
            return self.fail_response(f"Pipeline creation failed: {str(e)}")

    @openapi_schema({
        "type": "function",
        "function": {
            "name": "execute_data_pipeline",
            "description": "Execute a previously created data pipeline",
            "parameters": {
                "type": "object",
                "properties": {
                    "pipeline_name": {
                        "type": "string",
                        "description": "Name of the pipeline to execute"
                    },
                    "input_data": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "Input data for the pipeline"
                    }
                },
                "required": ["pipeline_name", "input_data"]
            }
        }
    })
    async def execute_data_pipeline(
        self, 
        pipeline_name: str, 
        input_data: List[Dict[str, Any]]
    ) -> ToolResult:
        """Execute a data processing pipeline."""
        try:
            if pipeline_name not in self.data_pipelines:
                return self.fail_response(f"Pipeline '{pipeline_name}' not found")
            
            pipeline = self.data_pipelines[pipeline_name]
            execution_start = datetime.now()
            
            # Execute pipeline steps
            current_data = input_data
            step_results = []
            
            for step in pipeline["processing_steps"]:
                step_start = datetime.now()
                
                # Execute the processing step
                step_result = await self.process_dataset(
                    data=current_data,
                    operations=[step],
                    include_statistics=False
                )
                
                step_end = datetime.now()
                step_duration = (step_end - step_start).total_seconds()
                
                if step_result.success:
                    step_results.append({
                        "step": step,
                        "duration": step_duration,
                        "status": "success",
                        "output_rows": len(current_data)
                    })
                    # Update current_data for next step if needed
                else:
                    step_results.append({
                        "step": step,
                        "duration": step_duration,
                        "status": "failed",
                        "error": step_result.output
                    })
                    break
            
            execution_end = datetime.now()
            total_duration = (execution_end - execution_start).total_seconds()
            
            # Update pipeline execution history
            execution_record = {
                "execution_id": f"{pipeline_name}_{int(execution_start.timestamp())}",
                "start_time": execution_start.isoformat(),
                "end_time": execution_end.isoformat(),
                "duration": total_duration,
                "input_rows": len(input_data),
                "steps_executed": len(step_results),
                "status": "completed" if all(s["status"] == "success" for s in step_results) else "failed",
                "step_results": step_results
            }
            
            pipeline["execution_history"].append(execution_record)
            pipeline["last_execution"] = execution_record
            
            return self.success_response({
                "pipeline_execution": execution_record,
                "pipeline_name": pipeline_name,
                "final_data_preview": current_data[:3] if current_data else []
            })
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}")
            return self.fail_response(f"Pipeline execution failed: {str(e)}")