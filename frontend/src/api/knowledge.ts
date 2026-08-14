import apiClient from './client';

export interface KnowledgeDocument {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  chunk_count: number;
  status: string;
  product_category: string | null;
  error_message: string | null;
  created_at: string;
}

export interface KBStats {
  total_documents: number;
  total_chunks: number;
  by_status: Record<string, number>;
  by_category: Record<string, number>;
}

export const knowledgeAPI = {
  upload: (file: File, productCategory: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('product_category', productCategory);
    return apiClient.post('/kb/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  list: (params?: { page?: number; size?: number; status?: string; product_category?: string }) =>
    apiClient.get<KnowledgeDocument[]>('/kb/documents', { params }),
  get: (id: string) =>
    apiClient.get<KnowledgeDocument>(`/kb/documents/${id}`),
  delete: (id: string) =>
    apiClient.delete(`/kb/documents/${id}`),
  stats: () =>
    apiClient.get<KBStats>('/kb/stats'),
};
