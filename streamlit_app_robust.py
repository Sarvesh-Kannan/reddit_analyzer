#!/usr/bin/env python3
"""
Indian Fashion Trend Analysis - Streamlit App (Robust Version)
Interactive UI for fashion trend analysis with LLM insights and web data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import requests
import logging
from datetime import datetime
from config import Config
from web_search_analyzer import WebSearchAnalyzer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FashionTrendApp:
    def __init__(self):
        self.cleaned_data = None
        self.analysis_results = None
        self.web_trends = None
        self.web_analyzer = WebSearchAnalyzer()
        self.load_data()
    
    def load_data(self):
        """Load cleaned data, analysis results, and web trends"""
        try:
            # Load cleaned data
            with open(f"{Config.OUTPUT_DIR}/cleaned_fashion_data.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.cleaned_data = data['posts']
            
            # Load analysis results if available
            try:
                with open(f"{Config.OUTPUT_DIR}/llm_analysis_results.json", 'r', encoding='utf-8') as f:
                    self.analysis_results = json.load(f)
            except FileNotFoundError:
                self.analysis_results = {}
            
            # Load web trends if available
            try:
                with open(f"{Config.OUTPUT_DIR}/web_trends.json", 'r', encoding='utf-8') as f:
                    self.web_trends = json.load(f)
            except FileNotFoundError:
                self.web_trends = {}
            
            logger.info("✅ Data loaded for Streamlit app")
            
        except Exception as e:
            logger.error(f"❌ Error loading data: {str(e)}")
            self.cleaned_data = []
            self.analysis_results = {}
            self.web_trends = {}
    
    def safe_create_chart(self, chart_type, data, **kwargs):
        """Safely create charts with error handling"""
        try:
            if chart_type == 'bar':
                return px.bar(data, **kwargs)
            elif chart_type == 'pie':
                return px.pie(data, **kwargs)
            elif chart_type == 'scatter':
                return px.scatter(data, **kwargs)
            else:
                return None
        except Exception as e:
            logger.error(f"❌ Error creating {chart_type} chart: {str(e)}")
            return None
    
    def call_ollama(self, prompt, max_tokens=2048):
        """Call Ollama API"""
        try:
            payload = {
                "model": "deepseek-r1:8b",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": max_tokens
                }
            }
            
            response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ Error calling Ollama: {str(e)}")
            return None
    
    def run_web_search(self):
        """Run web search analysis on demand"""
        if st.button("🔍 Run Web Search Analysis", type="secondary"):
            with st.spinner("Running web search analysis..."):
                try:
                    trends = self.web_analyzer.gather_comprehensive_trends()
                    if trends:
                        self.web_analyzer.save_web_trends(f"{Config.OUTPUT_DIR}/web_trends.json")
                        st.success("✅ Web search analysis completed!")
                        st.rerun()
                    else:
                        st.error("❌ Web search analysis failed.")
                except Exception as e:
                    st.error(f"❌ Web search error: {str(e)}")
    
    def run_llm_analysis(self):
        """Run LLM analysis on demand"""
        if st.button("🤖 Run LLM Analysis", type="primary"):
            with st.spinner("Running LLM analysis..."):
                try:
                    # Analyze trending keywords
                    all_keywords = []
                    for post in self.cleaned_data:
                        all_keywords.extend(post['keywords'])
                    
                    keyword_counts = pd.Series(all_keywords).value_counts()
                    top_keywords = keyword_counts.head(15).to_dict()
                    
                    # Get web trends if available
                    web_keywords = {}
                    if self.web_trends and 'trending_summary' in self.web_trends:
                        web_keywords = self.web_trends['trending_summary'].get('top_keywords', {})
                    
                    prompt = f"""
                    Analyze Indian fashion trends using both Reddit community data and current web search results:

                    REDDIT DATA (Community Trends):
                    Top Keywords: {list(top_keywords.keys())}
                    Keyword Counts: {top_keywords}

                    WEB SEARCH DATA (Current Trends):
                    Top Web Keywords: {list(web_keywords.keys())[:10] if web_keywords else 'No web data'}

                    Please provide:
                    1. What are the most trending Indian fashion items/styles?
                    2. Which traditional vs modern fashion elements are popular?
                    3. How do Reddit community trends compare to web search trends?
                    4. What does this indicate about current Indian fashion preferences?
                    5. Any regional or cultural patterns you notice?
                    6. Recommendations for fashion retailers/buyers based on these trends.

                    Provide detailed analysis with specific insights and actionable recommendations.
                    """
                    
                    analysis = self.call_ollama(prompt)
                    if analysis:
                        st.success("✅ LLM Analysis Completed!")
                        st.text_area("🤖 LLM Insights", analysis, height=300)
                    else:
                        st.error("❌ LLM analysis failed. Check if Ollama is running.")
                except Exception as e:
                    st.error(f"❌ LLM analysis error: {str(e)}")
    
    def create_dashboard(self):
        """Create the main dashboard"""
        st.set_page_config(
            page_title="Indian Fashion Trend Analysis",
            page_icon="🇮🇳",
            layout="wide"
        )
        
        # Header
        st.title("🇮🇳 Indian Fashion Trend Analysis")
        st.markdown("---")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Total Posts", len(self.cleaned_data))
        
        with col2:
            if self.cleaned_data:
                df = pd.DataFrame(self.cleaned_data)
                st.metric("📈 Avg Score", f"{df['score'].mean():.1f}")
            else:
                st.metric("📈 Avg Score", "N/A")
        
        with col3:
            if self.cleaned_data:
                unique_keywords = len(set([kw for post in self.cleaned_data for kw in post['keywords']]))
                st.metric("🏆 Top Keywords", unique_keywords)
            else:
                st.metric("🏆 Top Keywords", "N/A")
        
        with col4:
            if self.cleaned_data:
                df = pd.DataFrame(self.cleaned_data)
                st.metric("🗺️ Regions", df['region'].nunique())
            else:
                st.metric("🗺️ Regions", "N/A")
        
        st.markdown("---")
        
        # Main content
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Trending Keywords Chart
            st.subheader("🔥 Trending Keywords")
            if self.cleaned_data:
                try:
                    all_keywords = []
                    for post in self.cleaned_data:
                        all_keywords.extend(post['keywords'])
                    
                    keyword_counts = pd.Series(all_keywords).value_counts()
                    top_keywords = keyword_counts.head(15)
                    
                    if len(top_keywords) > 0:
                        fig = px.bar(
                            x=top_keywords.index,
                            y=top_keywords.values,
                            title="Top Trending Fashion Keywords",
                            labels={'x': 'Keywords', 'y': 'Count'},
                            color=top_keywords.values,
                            color_continuous_scale='viridis'
                        )
                        fig.update_layout(xaxis_tickangle=-45, height=400, showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No keyword data available")
                except Exception as e:
                    st.error(f"Error creating keywords chart: {str(e)}")
            
            # Regional Distribution
            st.subheader("🗺️ Regional Distribution")
            if self.cleaned_data:
                try:
                    df = pd.DataFrame(self.cleaned_data)
                    regional_counts = df['region'].value_counts()
                    
                    if len(regional_counts) > 0:
                        fig = px.pie(
                            values=regional_counts.values,
                            names=regional_counts.index,
                            title="Fashion Posts by Region"
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No regional data available")
                except Exception as e:
                    st.error(f"Error creating regional chart: {str(e)}")
        
        with col2:
            # Analysis Section
            st.subheader("🤖 Analysis Tools")
            self.run_llm_analysis()
            
            st.markdown("---")
            
            # Web Search Section
            st.subheader("🔍 Web Search")
            self.run_web_search()
            
            # Data Statistics
            st.subheader("📊 Data Statistics")
            if self.cleaned_data:
                try:
                    df = pd.DataFrame(self.cleaned_data)
                    
                    st.write(f"**Subreddits:** {df['subreddit'].nunique()}")
                    st.write(f"**Regions:** {df['region'].nunique()}")
                    st.write(f"**Avg Comments:** {df['num_comments'].mean():.1f}")
                    st.write(f"**Avg Upvote Ratio:** {df['upvote_ratio'].mean():.2f}")
                except Exception as e:
                    st.error(f"Error calculating statistics: {str(e)}")
            else:
                st.info("No data available for statistics")
        
        # Web vs Reddit Comparison
        if self.web_trends and 'trending_summary' in self.web_trends:
            st.markdown("---")
            st.subheader("📊 Web vs Reddit Trends Comparison")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Web keywords
                try:
                    web_summary = self.web_trends['trending_summary']
                    web_keywords = web_summary.get('top_keywords', {})
                    if web_keywords:
                        web_df = pd.DataFrame(list(web_keywords.items()), columns=['Keyword', 'Count'])
                        if len(web_df) > 0:
                            fig = px.bar(
                                web_df.head(10),
                                x='Keyword',
                                y='Count',
                                title="Top Web Search Keywords",
                                color='Count',
                                color_continuous_scale='plasma'
                            )
                            fig.update_layout(xaxis_tickangle=-45, height=300)
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No web keywords available")
                    else:
                        st.info("No web keywords data")
                except Exception as e:
                    st.error(f"Error creating web keywords chart: {str(e)}")
            
            with col2:
                # Reddit keywords
                if self.cleaned_data:
                    try:
                        all_keywords = []
                        for post in self.cleaned_data:
                            all_keywords.extend(post['keywords'])
                        
                        reddit_keyword_counts = pd.Series(all_keywords).value_counts()
                        reddit_df = pd.DataFrame(list(reddit_keyword_counts.head(10).items()), columns=['Keyword', 'Count'])
                        
                        if len(reddit_df) > 0:
                            fig = px.bar(
                                reddit_df,
                                x='Keyword',
                                y='Count',
                                title="Top Reddit Keywords",
                                color='Count',
                                color_continuous_scale='viridis'
                            )
                            fig.update_layout(xaxis_tickangle=-45, height=300)
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No Reddit keywords available")
                    except Exception as e:
                        st.error(f"Error creating Reddit keywords chart: {str(e)}")
        
        # Engagement Analysis
        st.markdown("---")
        st.subheader("📊 Engagement Analysis")
        
        if self.cleaned_data:
            try:
                df = pd.DataFrame(self.cleaned_data)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Score vs Comments scatter
                    if len(df) > 0:
                        fig = px.scatter(
                            df,
                            x='score',
                            y='num_comments',
                            color='subreddit',
                            title="Engagement: Score vs Comments",
                            labels={'score': 'Post Score', 'num_comments': 'Number of Comments'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No engagement data available")
                
                with col2:
                    # Top subreddits
                    if len(df) > 0:
                        subreddit_counts = df['subreddit'].value_counts()
                        if len(subreddit_counts) > 0:
                            fig = px.bar(
                                x=subreddit_counts.index,
                                y=subreddit_counts.values,
                                title="Posts by Subreddit",
                                labels={'x': 'Subreddit', 'y': 'Count'}
                            )
                            fig.update_layout(xaxis_tickangle=-45)
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No subreddit data available")
                    else:
                        st.info("No subreddit data available")
            except Exception as e:
                st.error(f"Error creating engagement charts: {str(e)}")
        
        # Web Trends Analysis
        if self.web_trends and 'trending_summary' in self.web_trends:
            st.markdown("---")
            st.subheader("🌐 Web Trends Analysis")
            
            try:
                web_summary = self.web_trends['trending_summary']
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Top brands
                    top_brands = web_summary.get('top_brands', {})
                    if top_brands:
                        brand_df = pd.DataFrame(list(top_brands.items()), columns=['Brand', 'Mentions'])
                        if len(brand_df) > 0:
                            fig = px.pie(
                                brand_df.head(8),
                                values='Mentions',
                                names='Brand',
                                title="Top Fashion Brands (Web)"
                            )
                            fig.update_layout(height=300)
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No brand data available")
                    else:
                        st.info("No brand data available")
                
                with col2:
                    # Top regions
                    top_regions = web_summary.get('top_regions', {})
                    if top_regions:
                        region_df = pd.DataFrame(list(top_regions.items()), columns=['Region', 'Mentions'])
                        if len(region_df) > 0:
                            fig = px.bar(
                                region_df.head(8),
                                x='Region',
                                y='Mentions',
                                title="Top Regions (Web)",
                                color='Mentions',
                                color_continuous_scale='teal'
                            )
                            fig.update_layout(xaxis_tickangle=-45, height=300)
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No region data available")
                    else:
                        st.info("No region data available")
                
                with col3:
                    # Top fabrics
                    top_fabrics = web_summary.get('top_fabrics', {})
                    if top_fabrics:
                        fabric_df = pd.DataFrame(list(top_fabrics.items()), columns=['Fabric', 'Mentions'])
                        if len(fabric_df) > 0:
                            fig = px.bar(
                                fabric_df.head(8),
                                x='Fabric',
                                y='Mentions',
                                title="Top Fabrics (Web)",
                                color='Mentions',
                                color_continuous_scale='sunset'
                            )
                            fig.update_layout(xaxis_tickangle=-45, height=300)
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No fabric data available")
                    else:
                        st.info("No fabric data available")
            except Exception as e:
                st.error(f"Error creating web trends charts: {str(e)}")
        
        # Data Table
        st.markdown("---")
        st.subheader("📋 Fashion Posts Data")
        
        if self.cleaned_data:
            try:
                df = pd.DataFrame(self.cleaned_data)
                display_df = df[['title', 'subreddit', 'score', 'region', 'keywords']].head(50)
                
                # Format keywords for display
                display_df['keywords'] = display_df['keywords'].apply(lambda x: ', '.join(x[:3]) if x else 'None')
                
                st.dataframe(display_df, use_container_width=True)
            except Exception as e:
                st.error(f"Error displaying data table: {str(e)}")
        else:
            st.info("No data available for display")
        
        # Interactive Analysis
        st.markdown("---")
        st.subheader("🔍 Interactive Analysis")
        
        if self.cleaned_data:
            try:
                df = pd.DataFrame(self.cleaned_data)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Filter by subreddit
                    subreddit_filter = st.selectbox(
                        "Select Subreddit",
                        ['All'] + list(df['subreddit'].unique())
                    )
                    
                    if subreddit_filter != 'All':
                        filtered_df = df[df['subreddit'] == subreddit_filter]
                    else:
                        filtered_df = df
                    
                    st.write(f"**Posts in {subreddit_filter}:** {len(filtered_df)}")
                    st.write(f"**Average Score:** {filtered_df['score'].mean():.1f}")
                
                with col2:
                    # Filter by region
                    region_filter = st.selectbox(
                        "Select Region",
                        ['All'] + list(df['region'].unique())
                    )
                    
                    if region_filter != 'All':
                        region_df = df[df['region'] == region_filter]
                    else:
                        region_df = df
                    
                    st.write(f"**Posts in {region_filter}:** {len(region_df)}")
                    st.write(f"**Average Score:** {region_df['score'].mean():.1f}")
            except Exception as e:
                st.error(f"Error in interactive analysis: {str(e)}")
        
        # Custom Analysis
        st.markdown("---")
        st.subheader("🎯 Custom Analysis")
        
        if st.button("🔍 Analyze High-Engagement Posts"):
            if self.cleaned_data:
                try:
                    df = pd.DataFrame(self.cleaned_data)
                    high_engagement = df[df['score'] > df['score'].quantile(0.8)]
                    
                    st.write(f"**High Engagement Posts (>80th percentile):** {len(high_engagement)}")
                    
                    # Show top posts
                    top_posts = high_engagement.nlargest(10, 'score')[['title', 'score', 'subreddit', 'keywords']]
                    st.dataframe(top_posts, use_container_width=True)
                except Exception as e:
                    st.error(f"Error analyzing high-engagement posts: {str(e)}")
        
        if st.button("📈 Analyze Keyword Trends"):
            if self.cleaned_data:
                try:
                    all_keywords = []
                    for post in self.cleaned_data:
                        all_keywords.extend(post['keywords'])
                    
                    keyword_counts = pd.Series(all_keywords).value_counts()
                    
                    st.write("**Top 20 Fashion Keywords:**")
                    for keyword, count in keyword_counts.head(20).items():
                        st.write(f"• {keyword}: {count} mentions")
                except Exception as e:
                    st.error(f"Error analyzing keyword trends: {str(e)}")

def main():
    """Main function to run the Streamlit app"""
    app = FashionTrendApp()
    app.create_dashboard()

if __name__ == "__main__":
    main() 