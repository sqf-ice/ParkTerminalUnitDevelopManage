-- 创建表
CREATE TABLE IF NOT EXISTS payload_json( JSON TEXT, UPLOAD_TIME TEXT);

--  上传失败则保存到数据库
INSERT INTO payload_json VALUES (payloadJson, time);

-- 查询数据库是否有内容
SELECT * FROM payload_json;

-- 重传成功则删除该条记录
DELETE FROM payload_json WHERE JSON= 'payloadJson';

