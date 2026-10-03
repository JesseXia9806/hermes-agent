#!/usr/bin/env python3
"""
数据分析模型技能集 - 主执行脚本
基于微信公众号《这9个分析模型，撑起了80%的数据分析工作》的实战技能集

使用方法:
    python main.py <analysis_type> [options]

支持的模型:
    problem-judgment    - 问题判断与模型选择
    comparison-analysis  - 对比分析
    trend-analysis      - 趋势分析
    structural-analysis  - 结构分析
    pareto-analysis     - Pareto分析
    funnel-analysis      - 漏斗分析
    cohort-analysis     - 同期群分析
    rfm-analysis        - RFM分析
    attribution-analysis - 归因分析
    ab-testing          - A/B测试验证

示例:
    python main.py problem-judgment --question "系统响应时间变慢了"
    python main.py comparison-analysis --data "performance.csv" --baseline "2025-01" --current "2026-01"
    python main.py trend-analysis --data "metrics.csv" --metric "response_time"
"""

import sys
import json
import argparse
from pathlib import Path

# 导入各个分析模块
try:
    from scripts.problem_judgment import ProblemJudgment
    from scripts.comparison_analysis import ComparisonAnalysis
    from scripts.trend_analysis import TrendAnalysis
    from scripts.structural_analysis import StructuralAnalysis
    from scripts.pareto_analysis import ParetoAnalysis
    from scripts.funnel_analysis import FunnelAnalysis
    from scripts.cohort_analysis import CohortAnalysis
    from scripts.rfm_analysis import RFMAnalysis
    from scripts.attribution_analysis import AttributionAnalysis
    from scripts.ab_testing import ABTesting
except ImportError as e:
    print(f"错误: 无法导入分析模块 - {e}")
    print("请确保所有脚本文件都在 scripts/ 目录中")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="数据分析模型技能集 - 基于9大分析模型的实战工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 问题判断
  python main.py problem-judgment --question "系统响应时间变慢了"
  
  # 对比分析
  python main.py comparison-analysis --data "performance.csv" --baseline "2025-01" --current "2026-01"
  
  # 趋势分析
  python main.py trend-analysis --data "metrics.csv" --metric "response_time" --period "30d"
  
  # Pareto分析
  python main.py pareto-analysis --data "errors.csv" --value "count" --category "type"
  
  # 漏斗分析
  python main.py funnel-analysis --data "conversion.csv" --stages "visit,register,purchase"
        """
    )
    
    parser.add_argument('analysis_type', 
                       choices=['problem-judgment', 'comparison-analysis', 'trend-analysis',
                               'structural-analysis', 'pareto-analysis', 'funnel-analysis',
                               'cohort-analysis', 'rfm-analysis', 'attribution-analysis', 'ab-testing'],
                       help='选择分析模型类型')
    
    parser.add_argument('--data-file', '-d', help='数据文件路径')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    # 通用参数
    parser.add_argument('--format', choices=['json', 'html'], default='json', help='输出格式')
    parser.add_argument('--save', action='store_true', help='保存结果到文件')
    
    args = parser.parse_args()
    
    try:
        # 初始化对应的分析器
        analyzer = None
        result = None
        
        if args.analysis_type == 'problem-judgment':
            analyzer = ProblemJudgment()
            result = analyzer.analyze()
            
        elif args.analysis_type == 'comparison-analysis':
            analyzer = ComparisonAnalysis(args.data_file)
            result = analyzer.analyze()
            
        elif args.analysis_type == 'trend-analysis':
            analyzer = TrendAnalysis(args.data_file)
            result = analyzer.analyze()
            
        elif args.analysis_type == 'structural-analysis':
            analyzer = StructuralAnalysis(args.data_file)
            result = analyzer.analyze()
            
        elif args.analysis_type == 'pareto-analysis':
            analyzer = ParetoAnalysis(args.data_file)
            result = analyzer.analyze()
            
        elif args.analysis_type == 'funnel-analysis':
            analyzer = FunnelAnalysis(args.data_file)
            result = analyzer.analyze()
            
        elif args.analysis_type == 'cohort-analysis':
            analyzer = CohortAnalysis(args.data_file)
            result = analyzer.analyze()
            
        elif args.analysis_type == 'rfm-analysis':
            analyzer = RFMAnalysis(args.data_file)
            result = analyzer.analyze()
            
        elif args.analysis_type == 'attribution-analysis':
            analyzer = AttributionAnalysis(args.data_file)
            result = analyzer.analyze()
            
        elif args.analysis_type == 'ab-testing':
            analyzer = ABTesting(args.data_file)
            result = analyzer.analyze()
        
        # 输出结果
        if args.format == 'json':
            output = json.dumps(result, indent=2, ensure_ascii=False)
        else:
            output = generate_html_report(result, args.analysis_type)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"结果已保存到: {args.output}")
        else:
            print(output)
            
        if args.verbose:
            print("\n" + "="*50)
            print("分析完成!")
            print(f"使用的模型: {args.analysis_type}")
            print(f"输出格式: {args.format}")
            
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)

def generate_html_report(result, analysis_type):
    """生成HTML格式的报告"""
    html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>数据分析报告 - {analysis_type}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f0f0f0; padding: 20px; margin-bottom: 20px; }}
        .section {{ margin-bottom: 20px; }}
        .metric {{ background: #e8f4f8; padding: 10px; margin: 5px 0; }}
        .recommendation {{ background: #fff3cd; padding: 10px; margin: 5px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>数据分析报告</h1>
        <p>分析类型: {analysis_type}</p>
        <p>生成时间: {result.get('timestamp', 'N/A')}</p>
    </div>
    
    <div class="section">
        <h2>分析结果</h2>
        <div class="metric">
            {json.dumps(result, indent=2, ensure_ascii=False)}
        </div>
    </div>
    
    <div class="section">
        <h2>建议</h2>
        <div class="recommendation">
            请根据分析结果采取相应的行动措施。
        </div>
    </div>
</body>
</html>
    """
    return html_template

if __name__ == "__main__":
    main()
"""