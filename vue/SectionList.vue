<template>
  <div>
    <el-row>
      <el-col :span="6" v-for="section in sections" :key="section.id">
        <el-card>
          <div slot="header" class="clearfix">
            <span>{{ section.name }}</span>
            <el-button @click="editSection(section.id)" size="mini" style="float: right;">编辑</el-button>
            <el-button @click="deleteSection(section.id)" size="mini" style="float: right; margin-right: 5px;">删除</el-button>
          </div>
          <div>{{ section.description }}</div>
        </el-card>
      </el-col>
    </el-row>
    <el-button @click="addSection" size="small" type="primary">添加小节</el-button>
  </div>
</template>

<script>
import { ElCard, ElButton, ElRow, ElCol } from 'element-ui';
import axios from 'axios';

export default {
  name: 'SectionList',
  components: {
    ElCard,
    ElButton,
    ElRow,
    ElCol
  },
  data() {
    return {
      chapterId: this.$route.params.chapterId, // 获取路由参数中的 chapterId
      sections: []
    };
  },
  methods: {
    async fetchSections() {
      const response = await axios.get(`/api/chapters/${this.chapterId}/sections`);
      this.sections = response.data;
    },
    async deleteSection(sectionId) {
      await axios.delete(`/api/sections/${sectionId}`);
      this.fetchSections(); // 删除后重新加载小节列表
    },
    editSection(sectionId) {
      // 打开编辑小节的界面
    },
    addSection() {
      const name = prompt("请输入小节名称");
      const description = prompt("请输入小节描述");
      if (name && description) {
        axios.post('/api/sections', {
          name: name,
          description: description,
          chapter_id: this.chapterId
        }).then(() => {
          this.fetchSections(); // 添加后重新加载小节列表
        });
      }
    }
  },
  mounted() {
    this.fetchSections();
  }
};
</script>
