<template>
  <div>
    <el-row>
      <el-col :span="6" v-for="module in modules" :key="module.id">
        <el-card>
          <div slot="header" class="clearfix">
            <span>{{ module.name }}</span>
            <el-button @click="editModule(module.id)" size="mini" style="float: right;">编辑</el-button>
            <el-button @click="deleteModule(module.id)" size="mini" style="float: right; margin-right: 5px;">删除</el-button>
          </div>
          <div>{{ module.description }}</div>
          <el-button @click="goToChapter(module.id)" size="mini">进入模块</el-button>
        </el-card>
      </el-col>
    </el-row>
    <el-button @click="addModule" size="small" type="primary">添加模块</el-button>
  </div>
</template>

<script>
import { ElCard, ElButton, ElRow, ElCol } from 'element-ui';
import axios from 'axios';

export default {
  name: 'ModuleList',
  components: {
    ElCard,
    ElButton,
    ElRow,
    ElCol
  },
  data() {
    return {
      courseId: this.$route.params.courseId, // 获取路由参数中的 courseId
      modules: []
    };
  },
  methods: {
    async fetchModules() {
      const response = await axios.get(`/api/courses/${this.courseId}/modules`);
      this.modules = response.data;
    },
    goToChapter(moduleId) {
      this.$router.push({ name: 'chapters', params: { moduleId } });
    },
    async deleteModule(moduleId) {
      await axios.delete(`/api/modules/${moduleId}`);
      this.fetchModules(); // 删除后重新加载模块列表
    },
    editModule(moduleId) {
      // 打开编辑模块的界面
    },
    addModule() {
      const name = prompt("请输入模块名称");
      const description = prompt("请输入模块描述");
      if (name && description) {
        axios.post('/api/modules', {
          name: name,
          description: description,
          course_id: this.courseId
        }).then(() => {
          this.fetchModules(); // 添加后重新加载模块列表
        });
      }
    }
  },
  mounted() {
    this.fetchModules();
  }
};
</script>
