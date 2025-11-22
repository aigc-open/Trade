# 文档 API 模块

## 功能说明

该模块提供通过后端 API 获取系统文档的功能，方便动态更新文档内容而无需重新构建前端。

## API 接口

### 1. 获取客户端埋点文档

**接口地址**: `/api/docs/client-tracking/`

**请求方法**: GET

**认证**: 需要 Token 认证

**响应示例**:
```json
{
  "content": "# 客户端埋点 API 调用指南\n...",
  "filename": "CLIENT_TRACKING_GUIDE.md",
  "last_modified": "2025-11-16T10:30:00"
}
```

### 2. 获取文档列表

**接口地址**: `/api/docs/list/`

**请求方法**: GET

**认证**: 需要 Token 认证

**响应示例**:
```json
[
  {
    "name": "客户端埋点API调用指南",
    "key": "client-tracking",
    "description": "详细的客户端埋点接口文档，包含所有模块的调用示例"
  }
]
```

## 如何添加新文档

1. 在项目根目录添加 Markdown 文档文件（例如：`NEW_DOC.md`）
2. 在 `views.py` 中添加新的 action 方法
3. 在前端 `api/index.js` 中添加对应的 API 调用方法
4. 在前端创建或修改页面来显示新文档

## 文档更新

只需直接修改服务器上的 Markdown 文件（如 `CLIENT_TRACKING_GUIDE.md`），前端刷新页面即可看到最新内容，无需重新部署前端。

## 优点

- ✅ 动态更新：修改文档无需重新部署前端
- ✅ 集中管理：所有文档统一由后端管理
- ✅ 版本追踪：显示文档最后修改时间
- ✅ 降级支持：API 失败时显示备用文档内容
- ✅ 认证保护：需要登录才能访问文档

