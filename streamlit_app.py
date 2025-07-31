#!/usr/bin/env python3
"""
Indian Fashion Trend Analysis - Streamlit App
Interactive UI for fashion trend analysis with LLM insights
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

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FashionTrendApp:
    def __init__(self):
        self.cleaned_data = None
        self.analysis_results = None
        self.load_data()
    
    def load_data(self):
        """Load cleaned data and analysis results"""
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
            
            logger.info("✅ Data loaded for Streamlit app")
            
        except Exception as e:
            logger.error(f"❌ Error loading data: {str(e)}")
            self.cleaned_data = []
            self.analysis_results = {}
    
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
    
    def run_analysis(self):
        """Run LLM analysis on demand"""
        if st.button("🤖 Run LLM Analysis", type="primary"):
            with st.spinner("Running LLM analysis..."):
                # Analyze trending keywords
                all_keywords = []
                for post in self.cleaned_data:
                    all_keywords.extend(post['keywords'])
                
                keyword_counts = pd.Series(all_keywords).value_counts()
                top_keywords = keyword_counts.head(15).to_dict()
                
                prompt = f"""
                Analyze the following Indian fashion keywords from Reddit data and provide insights:

                Top Keywords: {list(top_keywords.keys())}
                Keyword Counts: {top_keywords}

                Please provide:
                1. What are the most trending Indian fashion items/styles?
                2. Which traditional vs modern fashion elements are popular?
                3. What does this indicate about current Indian fashion preferences?
                4. Any regional or cultural patterns you notice?
                5. Recommendations for fashion retailers/buyers based on these trends.

                Provide detailed analysis with specific insights and actionable recommendations.
                """
                
                analysis = self.call_ollama(prompt)
                if analysis:
                    st.success("✅ LLM Analysis Completed!")
                    st.text_area("🤖 LLM Insights", analysis, height=300)
                else:
                    st.error("❌ LLM analysis failed. Check if Ollama is running.")
    
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
            df = pd.DataFrame(self.cleaned_data)
            st.metric("📈 Avg Score", f"{df['score'].mean():.1f}")
        
        with col3:
            st.metric("🏆 Top Keywords", len(set([kw for post in self.cleaned_data for kw in post['keywords']])))
        
        with col4:
            st.metric("🗺️ Regions", df['region'].nunique())
        
        st.markdown("---")
        
        # Main content
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Trending Keywords Chart
            st.subheader("🔥 Trending Keywords")
            if self.cleaned_data:
                all_keywords = []
                for post in self.cleaned_data:
                    all_keywords.extend(post['keywords'])
                
                keyword_counts = pd.Series(all_keywords).value_counts()
                top_keywords = keyword_counts.head(15)
                
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
            
            # Regional Distribution
            st.subheader("🗺️ Regional Distribution")
            if self.cleaned_data:
                df = pd.DataFrame(self.cleaned_data)
                regional_counts = df['region'].value_counts()
                
                fig = px.pie(
                    values=regional_counts.values,
                    names=regional_counts.index,
                    title="Fashion Posts by Region"
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # LLM Analysis Section
            st.subheader("🤖 LLM Analysis")
            self.run_analysis()
            
            # Data Statistics
            st.subheader("📊 Data Statistics")
            if self.cleaned_data:
                df = pd.DataFrame(self.cleaned_data)
                
                st.write(f"**Subreddits:** {df['subreddit'].nunique()}")
                st.write(f"**Regions:** {df['region'].nunique()}")
                st.write(f"**Avg Comments:** {df['num_comments'].mean():.1f}")
                st.write(f"**Avg Upvote Ratio:** {df['upvote_ratio'].mean():.2f}")
        
        # Engagement Analysis
        st.markdown("---")
        st.subheader("📊 Engagement Analysis")
        
        if self.cleaned_data:
            df = pd.DataFrame(self.cleaned_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Score vs Comments scatter
                fig = px.scatter(
                    df,
                    x='score',
                    y='num_comments',
                    color='subreddit',
                    title="Engagement: Score vs Comments",
                    labels={'score': 'Post Score', 'num_comments': 'Number of Comments'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Top subreddits
                subreddit_counts = df['subreddit'].value_counts()
                fig = px.bar(
                    x=subreddit_counts.index,
                    y=subreddit_counts.values,
                    title="Posts by Subreddit",
                    labels={'x': 'Subreddit', 'y': 'Count'}
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
        
        # Data Table
        st.markdown("---")
        st.subheader("📋 Fashion Posts Data")
        
        if self.cleaned_data:
            df = pd.DataFrame(self.cleaned_data)
            display_df = df[['title', 'subreddit', 'score', 'region', 'keywords']].head(50)
            
            # Format keywords for display
            display_df['keywords'] = display_df['keywords'].apply(lambda x: ', '.join(x[:3]) if x else 'None')
            
            st.dataframe(display_df, use_container_width=True)
        
        # Interactive Analysis
        st.markdown("---")
        st.subheader("🔍 Interactive Analysis")
        
        if self.cleaned_data:
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
        
        # Custom Analysis
        st.markdown("---")
        st.subheader("🎯 Custom Analysis")
        
        if st.button("🔍 Analyze High-Engagement Posts"):
            if self.cleaned_data:
                df = pd.DataFrame(self.cleaned_data)
                high_engagement = df[df['score'] > df['score'].quantile(0.8)]
                
                st.write(f"**High Engagement Posts (>80th percentile):** {len(high_engagement)}")
                
                # Show top posts
                top_posts = high_engagement.nlargest(10, 'score')[['title', 'score', 'subreddit', 'keywords']]
                st.dataframe(top_posts, use_container_width=True)
        
        if st.button("📈 Analyze Keyword Trends"):
            if self.cleaned_data:
                all_keywords = []
                for post in self.cleaned_data:
                    all_keywords.extend(post['keywords'])
                
                keyword_counts = pd.Series(all_keywords).value_counts()
                
                st.write("**Top 20 Fashion Keywords:**")
                for keyword, count in keyword_counts.head(20).items():
                    st.write(f"• {keyword}: {count} mentions")

def main():
    """Main function to run the Streamlit app"""
    app = FashionTrendApp()
    app.create_dashboard()

if __name__ == "__main__":
    main() 