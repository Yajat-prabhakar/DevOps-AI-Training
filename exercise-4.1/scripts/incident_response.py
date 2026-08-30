#!/usr/bin/env python3
"""
Incident Response Automation Scripts
Exercise 4.1: Complete Incident Response Automation

This script provides automated incident detection, analysis, and response.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import time
import threading
import random
import requests
from typing import Dict, List, Optional
import sys


class IncidentDetector:
    """Detects incidents from metrics and alerts"""
    
    def __init__(self):
        self.alerts = []
        self.incidents = []
    
    def detect_from_alerts(self, alerts: List[Dict]) -> List[Dict]:
        """Detect incidents from alerts"""
        incidents = []
        
        for alert in alerts:
            incident = {
                'id': f"INC-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
                'alert': alert['alertname'],
                'severity': alert.get('severity', 'unknown'),
                'service': alert.get('service', 'unknown'),
                'timestamp': datetime.now().isoformat(),
                'status': 'detected',
                'description': alert.get('description', 'No description')
            }
            incidents.append(incident)
        
        return incidents
    
    def detect_from_metrics(self, metrics: Dict) -> List[Dict]:
        """Detect incidents from metrics"""
        incidents = []
        
        # Check CPU
        if metrics.get('cpu', 0) > 90:
            incidents.append({
                'id': f"INC-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
                'alert': 'HighCpuUsage',
                'severity': 'critical',
                'service': 'system',
                'timestamp': datetime.now().isoformat(),
                'status': 'detected',
                'description': f'CPU usage is {metrics["cpu"]:.1f}%'
            })
        
        # Check memory
        if metrics.get('memory', 0) > 90:
            incidents.append({
                'id': f"INC-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
                'alert': 'HighMemoryUsage',
                'severity': 'critical',
                'service': 'system',
                'timestamp': datetime.now().isoformat(),
                'status': 'detected',
                'description': f'Memory usage is {metrics["memory"]:.1f}%'
            })
        
        # Check error rate
        if metrics.get('error_rate', 0) > 0.05:
            incidents.append({
                'id': f"INC-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
                'alert': 'HighErrorRate',
                'severity': 'warning',
                'service': 'application',
                'timestamp': datetime.now().isoformat(),
                'status': 'detected',
                'description': f'Error rate is {metrics["error_rate"]:.1%}'
            })
        
        # Check latency
        if metrics.get('latency_p95', 0) > 2:
            incidents.append({
                'id': f"INC-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
                'alert': 'HighLatency',
                'severity': 'warning',
                'service': 'application',
                'timestamp': datetime.now().isoformat(),
                'status': 'detected',
                'description': f'p95 latency is {metrics["latency_p95"]:.2f}s'
            })
        
        return incidents


class IncidentAnalyzer:
    """Analyzes incidents using AI"""
    
    def __init__(self):
        self.analysis_results = {}
    
    def analyze(self, incident: Dict) -> Dict:
        """Analyze incident and determine root cause"""
        print(f"Analyzing incident {incident['id']}...")
        
        # Simulate Claude analysis
        analysis = {
            'incident_id': incident['id'],
            'root_cause': self._determine_root_cause(incident),
            'confidence': random.uniform(0.7, 0.95),
            'affected_services': self._identify_affected_services(incident),
            'impact_assessment': self._assess_impact(incident),
            'recommended_actions': self._recommend_actions(incident),
            'timestamp': datetime.now().isoformat()
        }
        
        self.analysis_results[incident['id']] = analysis
        return analysis
    
    def _determine_root_cause(self, incident: Dict) -> str:
        """Determine root cause"""
        root_causes = {
            'HighCpuUsage': 'Runaway process or DDoS attack',
            'HighMemoryUsage': 'Memory leak or large data processing',
            'HighErrorRate': 'Application bug or dependency failure',
            'HighLatency': 'Database query performance or network issues'
        }
        return root_causes.get(incident['alert'], 'Unknown root cause')
    
    def _identify_affected_services(self, incident: Dict) -> List[str]:
        """Identify affected services"""
        service_map = {
            'HighCpuUsage': ['backend', 'database'],
            'HighMemoryUsage': ['backend', 'cache'],
            'HighErrorRate': ['backend', 'api-gateway'],
            'HighLatency': ['backend', 'database', 'cache']
        }
        return service_map.get(incident['alert'], ['unknown'])
    
    def _assess_impact(self, incident: Dict) -> Dict:
        """Assess impact"""
        impact_map = {
            'critical': {'users': 1000, 'revenue': 10000, 'severity': 'high'},
            'warning': {'users': 100, 'revenue': 1000, 'severity': 'medium'},
            'info': {'users': 10, 'revenue': 100, 'severity': 'low'}
        }
        return impact_map.get(incident['severity'], {'users': 0, 'revenue': 0, 'severity': 'unknown'})
    
    def _recommend_actions(self, incident: Dict) -> List[str]:
        """Recommend actions"""
        actions_map = {
            'HighCpuUsage': [
                'Check for runaway processes',
                'Review recent deployments',
                'Scale up instances'
            ],
            'HighMemoryUsage': [
                'Check for memory leaks',
                'Review application logs',
                'Add more memory'
            ],
            'HighErrorRate': [
                'Check application logs',
                'Review recent changes',
                'Rollback if needed'
            ],
            'HighLatency': [
                'Check database queries',
                'Review network latency',
                'Optimize slow queries'
            ]
        }
        return actions_map.get(incident['alert'], ['Investigate further'])


class IncidentResponder:
    """Responds to incidents automatically"""
    
    def __init__(self):
        self.responses = {}
    
    def respond(self, incident: Dict, analysis: Dict) -> Dict:
        """Respond to incident"""
        print(f"Responding to incident {incident['id']}...")
        
        response = {
            'incident_id': incident['id'],
            'actions_taken': self._take_actions(incident, analysis),
            'status': 'resolved',
            'resolution': self._determine_resolution(incident, analysis),
            'timestamp': datetime.now().isoformat()
        }
        
        self.responses[incident['id']] = response
        return response
    
    def _take_actions(self, incident: Dict, analysis: Dict) -> List[str]:
        """Take automated actions"""
        actions = []
        
        # Simulate automated actions
        if incident['alert'] == 'HighCpuUsage':
            actions.append('Scaled up instances')
            actions.append('Restarted runaway process')
        
        elif incident['alert'] == 'HighMemoryUsage':
            actions.append('Cleared cache')
            actions.append('Restarted application')
        
        elif incident['alert'] == 'HighErrorRate':
            actions.append('Rolled back deployment')
            actions.append('Enabled circuit breaker')
        
        elif incident['alert'] == 'HighLatency':
            actions.append('Optimized database queries')
            actions.append('Added caching')
        
        return actions
    
    def _determine_resolution(self, incident: Dict, analysis: Dict) -> str:
        """Determine resolution"""
        resolutions = {
            'HighCpuUsage': 'Identified and killed runaway process',
            'HighMemoryUsage': 'Fixed memory leak in application code',
            'HighErrorRate': 'Rolled back faulty deployment',
            'HighLatency': 'Optimized slow database queries'
        }
        return resolutions.get(incident['alert'], 'Issue investigated and mitigated')


class IncidentDocumenter:
    """Documents incidents and generates reports"""
    
    def __init__(self):
        self.reports = {}
    
    def generate_post_incident_report(self, incident: Dict, analysis: Dict, 
                                     response: Dict) -> Dict:
        """Generate post-incident report"""
        report = {
            'incident_id': incident['id'],
            'summary': {
                'severity': incident['severity'],
                'duration': '45 minutes',
                'impact': analysis['impact_assessment'],
                'root_cause': analysis['root_cause']
            },
            'timeline': self._generate_timeline(incident, analysis, response),
            'root_cause_analysis': analysis,
            'resolution': response['resolution'],
            'lessons_learned': self._generate_lessons_learned(incident, analysis),
            'action_items': self._generate_action_items(incident, analysis),
            'timestamp': datetime.now().isoformat()
        }
        
        self.reports[incident['id']] = report
        return report
    
    def _generate_timeline(self, incident: Dict, analysis: Dict, 
                          response: Dict) -> List[Dict]:
        """Generate timeline"""
        base_time = datetime.now() - timedelta(minutes=45)
        
        timeline = [
            {'time': base_time.isoformat(), 'event': 'Incident detected'},
            {'time': (base_time + timedelta(minutes=5)).isoformat(), 'event': 'Analysis started'},
            {'time': (base_time + timedelta(minutes=15)).isoformat(), 'event': 'Root cause identified'},
            {'time': (base_time + timedelta(minutes=20)).isoformat(), 'event': 'Response actions initiated'},
            {'time': (base_time + timedelta(minutes=35)).isoformat(), 'event': 'Resolution validated'},
            {'time': (base_time + timedelta(minutes=45)).isoformat(), 'event': 'Incident closed'}
        ]
        
        return timeline
    
    def _generate_lessons_learned(self, incident: Dict, analysis: Dict) -> List[str]:
        """Generate lessons learned"""
        lessons = [
            'Need better monitoring for this failure mode',
            'Automated response was effective',
            'Communication could be improved',
            'Need to update runbooks'
        ]
        return lessons
    
    def _generate_action_items(self, incident: Dict, analysis: Dict) -> List[Dict]:
        """Generate action items"""
        action_items = [
            {
                'action': 'Add monitoring for this failure mode',
                'owner': 'SRE Team',
                'priority': 'high',
                'due_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            },
            {
                'action': 'Update incident response runbook',
                'owner': 'DevOps Team',
                'priority': 'medium',
                'due_date': (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
            },
            {
                'action': 'Improve automated testing',
                'owner': 'Engineering Team',
                'priority': 'medium',
                'due_date': (datetime.now() + timedelta(days=21)).strftime('%Y-%m-%d')
            }
        ]
        return action_items


def main():
    """Main function"""
    print("=" * 60)
    print("Exercise 4.1: Complete Incident Response Automation")
    print("=" * 60)
    
    # Simulate metrics
    print("\n1. Simulating metrics...")
    metrics = {
        'cpu': 95,
        'memory': 75,
        'error_rate': 0.08,
        'latency_p95': 3.5
    }
    print(f"   CPU: {metrics['cpu']}%")
    print(f"   Memory: {metrics['memory']}%")
    print(f"   Error Rate: {metrics['error_rate']:.1%}")
    print(f"   Latency p95: {metrics['latency_p95']}s")
    
    # Detect incidents
    print("\n2. Detecting incidents...")
    detector = IncidentDetector()
    incidents = detector.detect_from_metrics(metrics)
    print(f"   Detected {len(incidents)} incidents")
    
    # Analyze incidents
    print("\n3. Analyzing incidents...")
    analyzer = IncidentAnalyzer()
    for incident in incidents:
        analysis = analyzer.analyze(incident)
        print(f"   {incident['id']}: {analysis['root_cause']}")
    
    # Respond to incidents
    print("\n4. Responding to incidents...")
    responder = IncidentResponder()
    for incident in incidents:
        analysis = analyzer.analysis_results[incident['id']]
        response = responder.respond(incident, analysis)
        print(f"   {incident['id']}: {response['resolution']}")
    
    # Generate reports
    print("\n5. Generating post-incident reports...")
    documenter = IncidentDocumenter()
    for incident in incidents:
        analysis = analyzer.analysis_results[incident['id']]
        response = responder.responses[incident['id']]
        report = documenter.generate_post_incident_report(incident, analysis, response)
        print(f"   {incident['id']}: Report generated")
    
    # Save reports
    print("\n6. Saving reports...")
    for incident_id, report in documenter.reports.items():
        filename = f"post-incident-report-{incident_id}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"   Saved {filename}")
    
    print("\n" + "=" * 60)
    print("Incident Response Automation Complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
