"""Enhanced watsonx.ai client with validation, retry logic, and metrics collection.

This module extends the base watsonx_client.py with Phase 2 improvements:
- Response validation and quality scoring
- Automatic retry with prompt refinement
- Metrics collection and analysis
- Advanced prompt template system
"""

import os
import time
from typing import Generator, Optional, Tuple
from watsonx_client import (
    _get_iam_token,
    _build_prompt,
    _generate_stream as _base_generate_stream,
    _get_profile
)
from src.utils.response_validator import ResponseValidator, ValidationResult
from src.utils.metrics_collector import get_metrics_collector
from src.utils.prompt_templates import get_template_manager, PromptVersion


class EnhancedWatsonXClient:
    """Enhanced watsonx.ai client with validation and retry logic."""
    
    def __init__(
        self,
        enable_validation: bool = True,
        enable_metrics: bool = True,
        enable_retry: bool = True,
        max_retries: int = 2,
        min_quality_threshold: float = 0.7
    ):
        """Initialize enhanced client.
        
        Args:
            enable_validation: Enable response validation
            enable_metrics: Enable metrics collection
            enable_retry: Enable automatic retry on low quality
            max_retries: Maximum number of retries
            min_quality_threshold: Minimum quality score (0.0 to 1.0)
        """
        self.enable_validation = enable_validation
        self.enable_metrics = enable_metrics
        self.enable_retry = enable_retry
        self.max_retries = max_retries
        self.min_quality_threshold = min_quality_threshold
        
        self.validator = ResponseValidator() if enable_validation else None
        self.metrics_collector = get_metrics_collector() if enable_metrics else None
        self.template_manager = get_template_manager()
    
    def generate_docs_with_validation(
        self,
        code: str,
        language: str = "Python",
        prompt_version: Optional[PromptVersion] = None
    ) -> Tuple[str, Optional[ValidationResult]]:
        """Generate documentation with validation and retry logic.
        
        Args:
            code: Source code to document
            language: Programming language
            prompt_version: Prompt template version to use
            
        Returns:
            Tuple of (generated_output, validation_result)
        """
        profile = _get_profile(language)
        retry_count = 0
        start_time = time.time()
        
        while retry_count <= self.max_retries:
            # Get prompt from template manager
            system, user = self.template_manager.get_docs_prompt(
                code=code,
                language=language,
                doc_style=profile['doc_style'],
                style_guide=profile['style_guide'],
                version=prompt_version,
                include_examples=(retry_count == 0)  # Include examples on first try
            )
            
            # Generate response
            prompt = _build_prompt(system, user)
            response = "".join(_base_generate_stream(
                prompt,
                max_tokens=8000,
                temperature=0.25 + (retry_count * 0.05),  # Increase temp on retry
                min_tokens=800
            ))
            
            # Validate if enabled
            if self.enable_validation and self.validator:
                validation = self.validator.validate_documentation(response, code, language)
                
                # Record metrics
                if self.enable_metrics and self.metrics_collector:
                    duration = time.time() - start_time
                    self.metrics_collector.record(
                        action="docs",
                        language=language,
                        duration=duration,
                        input_tokens=int(len(prompt.split()) * 1.3),  # Rough estimate
                        output_tokens=int(len(response.split()) * 1.3),
                        quality_score=validation.quality_score,
                        success=validation.is_valid,
                        retry_count=retry_count
                    )
                
                # Check if quality is acceptable
                if validation.quality_score >= self.min_quality_threshold:
                    return response, validation
                
                # If retry is disabled or max retries reached, return anyway
                if not self.enable_retry or retry_count >= self.max_retries:
                    return response, validation
                
                # Prepare for retry
                retry_count += 1
                print(f"Quality score {validation.quality_score:.2f} below threshold. Retrying ({retry_count}/{self.max_retries})...")
            else:
                # No validation, return immediately
                if self.enable_metrics and self.metrics_collector:
                    duration = time.time() - start_time
                    self.metrics_collector.record(
                        action="docs",
                        language=language,
                        duration=duration,
                        input_tokens=int(len(prompt.split()) * 1.3),
                        output_tokens=int(len(response.split()) * 1.3),
                        quality_score=1.0,
                        success=True,
                        retry_count=0
                    )
                return response, None
        
        # Max retries reached - should never reach here but added for type safety
        return "", None
    
    def generate_tests_with_validation(
        self,
        code: str,
        language: str = "Python",
        prompt_version: Optional[PromptVersion] = None
    ) -> Tuple[str, Optional[ValidationResult]]:
        """Generate tests with validation and retry logic.
        
        Args:
            code: Source code to test
            language: Programming language
            prompt_version: Prompt template version to use
            
        Returns:
            Tuple of (generated_output, validation_result)
        """
        profile = _get_profile(language)
        retry_count = 0
        start_time = time.time()
        
        while retry_count <= self.max_retries:
            # Get prompt from template manager
            system, user = self.template_manager.get_tests_prompt(
                code=code,
                language=language,
                test_framework=profile['test_framework'],
                test_conventions=profile['test_conventions'],
                import_style=profile['import_style'],
                version=prompt_version,
                include_examples=(retry_count == 0)
            )
            
            # Generate response
            prompt = _build_prompt(system, user)
            response = "".join(_base_generate_stream(
                prompt,
                max_tokens=8000,
                temperature=0.25 + (retry_count * 0.05),
                min_tokens=1000
            ))
            
            # Validate if enabled
            if self.enable_validation and self.validator:
                validation = self.validator.validate_tests(response, code, language)
                
                # Record metrics
                if self.enable_metrics and self.metrics_collector:
                    duration = time.time() - start_time
                    self.metrics_collector.record(
                        action="tests",
                        language=language,
                        duration=duration,
                        input_tokens=int(len(prompt.split()) * 1.3),
                        output_tokens=int(len(response.split()) * 1.3),
                        quality_score=validation.quality_score,
                        success=validation.is_valid,
                        retry_count=retry_count
                    )
                
                # Check if quality is acceptable
                if validation.quality_score >= self.min_quality_threshold:
                    return response, validation
                
                # If retry is disabled or max retries reached, return anyway
                if not self.enable_retry or retry_count >= self.max_retries:
                    return response, validation
                
                # Prepare for retry
                retry_count += 1
                print(f"Quality score {validation.quality_score:.2f} below threshold. Retrying ({retry_count}/{self.max_retries})...")
            else:
                # No validation, return immediately
                if self.enable_metrics and self.metrics_collector:
                    duration = time.time() - start_time
                    self.metrics_collector.record(
                        action="tests",
                        language=language,
                        duration=duration,
                        input_tokens=int(len(prompt.split()) * 1.3),
                        output_tokens=int(len(response.split()) * 1.3),
                        quality_score=1.0,
                        success=True,
                        retry_count=0
                    )
                return response, None
        
        # Max retries reached - should never reach here but added for type safety
        return "", None
    
    def stream_docs_with_monitoring(
        self,
        code: str,
        language: str = "Python",
        prompt_version: Optional[PromptVersion] = None
    ) -> Generator[str, None, None]:
        """Stream documentation generation with quality monitoring.
        
        Args:
            code: Source code to document
            language: Programming language
            prompt_version: Prompt template version to use
            
        Yields:
            Text chunks as they arrive
        """
        profile = _get_profile(language)
        start_time = time.time()
        
        # Get prompt from template manager
        system, user = self.template_manager.get_docs_prompt(
            code=code,
            language=language,
            doc_style=profile['doc_style'],
            style_guide=profile['style_guide'],
            version=prompt_version
        )
        
        # Stream response
        prompt = _build_prompt(system, user)
        full_response = []
        
        for chunk in _base_generate_stream(prompt, max_tokens=8000, temperature=0.25, min_tokens=800):
            full_response.append(chunk)
            yield chunk
        
        # Validate and record metrics after streaming completes
        response = "".join(full_response)
        
        if self.enable_validation and self.validator:
            validation = self.validator.validate_documentation(response, code, language)
            
            if self.enable_metrics and self.metrics_collector:
                duration = time.time() - start_time
                self.metrics_collector.record(
                    action="docs_stream",
                    language=language,
                    duration=duration,
                    input_tokens=int(len(prompt.split()) * 1.3),
                    output_tokens=int(len(response.split()) * 1.3),
                    quality_score=validation.quality_score,
                    success=validation.is_valid,
                    retry_count=0
                )
    
    def stream_tests_with_monitoring(
        self,
        code: str,
        language: str = "Python",
        prompt_version: Optional[PromptVersion] = None
    ) -> Generator[str, None, None]:
        """Stream test generation with quality monitoring.
        
        Args:
            code: Source code to test
            language: Programming language
            prompt_version: Prompt template version to use
            
        Yields:
            Text chunks as they arrive
        """
        profile = _get_profile(language)
        start_time = time.time()
        
        # Get prompt from template manager
        system, user = self.template_manager.get_tests_prompt(
            code=code,
            language=language,
            test_framework=profile['test_framework'],
            test_conventions=profile['test_conventions'],
            import_style=profile['import_style'],
            version=prompt_version
        )
        
        # Stream response
        prompt = _build_prompt(system, user)
        full_response = []
        
        for chunk in _base_generate_stream(prompt, max_tokens=8000, temperature=0.25, min_tokens=1000):
            full_response.append(chunk)
            yield chunk
        
        # Validate and record metrics after streaming completes
        response = "".join(full_response)
        
        if self.enable_validation and self.validator:
            validation = self.validator.validate_tests(response, code, language)
            
            if self.enable_metrics and self.metrics_collector:
                duration = time.time() - start_time
                self.metrics_collector.record(
                    action="tests_stream",
                    language=language,
                    duration=duration,
                    input_tokens=int(len(prompt.split()) * 1.3),
                    output_tokens=int(len(response.split()) * 1.3),
                    quality_score=validation.quality_score,
                    success=validation.is_valid,
                    retry_count=0
                )
    
    def get_metrics_summary(self) -> dict:
        """Get summary of collected metrics.
        
        Returns:
            Dictionary with metrics summary
        """
        if self.enable_metrics and self.metrics_collector:
            return self.metrics_collector.get_summary()
        return {}
    
    def get_quality_trends(self) -> dict:
        """Get quality score trends.
        
        Returns:
            Dictionary with quality trend analysis
        """
        if self.enable_metrics and self.metrics_collector:
            return self.metrics_collector.get_quality_trends()
        return {}


# Convenience functions for backward compatibility

def generate_docs_enhanced(
    code: str,
    language: str = "Python",
    enable_validation: bool = True,
    enable_retry: bool = True
) -> Tuple[str, Optional[ValidationResult]]:
    """Generate documentation with validation and retry.
    
    Args:
        code: Source code to document
        language: Programming language
        enable_validation: Enable response validation
        enable_retry: Enable automatic retry on low quality
        
    Returns:
        Tuple of (generated_output, validation_result)
    """
    client = EnhancedWatsonXClient(
        enable_validation=enable_validation,
        enable_retry=enable_retry
    )
    return client.generate_docs_with_validation(code, language)


def generate_tests_enhanced(
    code: str,
    language: str = "Python",
    enable_validation: bool = True,
    enable_retry: bool = True
) -> Tuple[str, Optional[ValidationResult]]:
    """Generate tests with validation and retry.
    
    Args:
        code: Source code to test
        language: Programming language
        enable_validation: Enable response validation
        enable_retry: Enable automatic retry on low quality
        
    Returns:
        Tuple of (generated_output, validation_result)
    """
    client = EnhancedWatsonXClient(
        enable_validation=enable_validation,
        enable_retry=enable_retry
    )
    return client.generate_tests_with_validation(code, language)


def stream_docs_enhanced(
    code: str,
    language: str = "Python"
) -> Generator[str, None, None]:
    """Stream documentation generation with monitoring.
    
    Args:
        code: Source code to document
        language: Programming language
        
    Yields:
        Text chunks as they arrive
    """
    client = EnhancedWatsonXClient()
    yield from client.stream_docs_with_monitoring(code, language)


def stream_tests_enhanced(
    code: str,
    language: str = "Python"
) -> Generator[str, None, None]:
    """Stream test generation with monitoring.
    
    Args:
        code: Source code to test
        language: Programming language
        
    Yields:
        Text chunks as they arrive
    """
    client = EnhancedWatsonXClient()
    yield from client.stream_tests_with_monitoring(code, language)

# Made with Bob
