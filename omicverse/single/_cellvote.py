

class CellVote(object):

    def __init__(self,adata) -> None:
        self.adata=adata

    def popv_anno(self):
        pass

    def scsa_anno(self):
        pass

    def gpt_anno(self):
        pass 

    def gbi_anno(self):
        pass 

    def scMulan_anno(self):
        pass

    def vote(self,
             clusters_key=None,
             cluster_markers=None,
             celltype_keys=[],
             model='gpt-3.5-turbo',
             base_url=None,
             species='human',
             organization='stomach',
             provider='openai'):
        
        
        cluster_celltypes={}
        adata=self.adata
        adata.obs['best_clusters']=adata.obs[clusters_key]
        adata.obs['best_clusters']=adata.obs['best_clusters'].astype('category')
        for ct in adata.obs['best_clusters'].cat.categories:
            ct_li=[]
            for celltype_key in celltype_keys:
                ct1=adata.obs.loc[adata.obs['best_clusters']==ct,celltype_key].value_counts().index[0]
                ct_li.append(ct1)

            cluster_celltypes[ct]=ct_li
        
        result = get_cluster_celltype(cluster_celltypes, cluster_markers, 
                              species=species, organization=organization,
                             model=model,base_url=base_url,provider=provider)
        return result



def get_cluster_celltype(cluster_celltypes, cluster_markers, species, organization,
                        model,base_url,provider,api_key=None):
    #from openai import OpenAI
    import os
    import numpy as np
    import pandas as pd
    import requests as requests
    if base_url is None:
        if provider == 'openai':
            base_url = "https://api.openai.com/v1"
        elif provider == 'kimi':
            base_url = "https://api.moonshot.cn/v1"
        elif provider == 'qwen':
            base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    if not api_key is None:
        QWEN_API_KEY = api_key
    else:
        QWEN_API_KEY = os.getenv("AGI_API_KEY")
    
    
    # 在这里配置您在本站的API_KEY
    api_key = QWEN_API_KEY
    
    headers = {
        "Authorization": 'Bearer ' + api_key,
    }
    cluster_celltype = {}
    from tqdm import tqdm
    for cluster_id, celltypes in tqdm(cluster_celltypes.items()):
        markers = cluster_markers.get(cluster_id, [])
        question = (
                    f"Given the species: {species} and organization: {organization}, "
                    f"determine the most suitable cell type for cluster {cluster_id}. "
                    f"The possible cell types are: {', '.join(celltypes)}. "
                    f"The gene markers for this cluster are: {', '.join(markers)}. "
                    f"Which cell type best represents this cluster? "
                    f"Only provide the cell type name. Do not show numbers before the name. Some can be a mixture of multiple cell types."
                    f"Do not provide the plural form of celltype."
                )
        #print(question)
        
        params = {
            "messages": [
        
                {
                    "role": 'user',
                    "content": question
                }
            ],
            # 如果需要切换模型，在这里修改
            "model": model
        }
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=params,
            stream=False
        )
        res = response.json()
        answer = res['choices'][0]['message']['content'].split('\n')
        # 将回答加入结果字典
        cluster_celltype[cluster_id] = answer[0].lower()
    
    return cluster_celltype