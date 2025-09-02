-- 更新项目状态值，使其与 ProjectStatus 枚举一致

-- 将 '在研' 更新为 '进行中'
UPDATE projects SET status = '进行中' WHERE status = '在研';

-- 将 '延期' 更新为 '已暂停'
UPDATE projects SET status = '已暂停' WHERE status = '延期';

-- 将 '结题' 更新为 '已完成'
UPDATE projects SET status = '已完成' WHERE status = '结题';