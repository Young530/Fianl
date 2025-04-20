<template>
  <div>
    <el-row>
      <el-col :span="6" v-for="chapter in chapters" :key="chapter.id">
        <el-card>
          <div slot="header" class="clearfix">
            <span>{{ chapter.name }}</span>
            <el-button @click="editChapter(chapter.id)" size="mini" style="float: right;">编辑</el-button>
            <el-button @click="deleteChapter(chapter.id)" size="mini" style="float: right; margin-right: 5px;">删除</el-button>
          </div>
          <div>{{ chapter.description }}</div>
          <el-button @click="goToSection(chapter.id)" size="mini">进入章节</el-button>
        </el-card>
      </el-col>
    </el-row>
    <el-button @click="addChapter" size="small" type="primary">添加章节</el-button>
  </div>
</template>

<script>
import { ElCard, ElButton, ElRow, ElCol } from 'element-ui';
import axios from 'axios';

export default {
  name: 'ChapterList',
  components: {
    ElCard,
    ElButton,
    ElRow,
    ElCol
  },
  data() {
    return {
      moduleId: this.$route.params.moduleId, // 获取路由参数中的 moduleId
      chapters: []
    };
  },
  methods: {
    async fetchChapters() {
      const response = await axios.get(`/api/modules/${this.moduleId}/chapters`);
      this.chapters = response.data;
    },
    goToSection(chapterId) {
      this.$router.push({ name: 'sections', params: { chapterId } });
    },
    async deleteChapter(chapterId) {
      await axios.delete(`/api/chapters/${chapterId}`);
      this.fetchChapters(); // 删除后重新加载章节列表
    },
    editChapter(chapterId) {
      // 打开编辑章节的界面
    },
    addChapter() {
      const name = prompt("请输入章节名称");
      const description = prompt("请输入章节描述");
      if (name && description) {
        axios.post('/api/chapters', {
          name: name,
          description: description,
          module_id: this.moduleId
        }).then(() => {
          this.fetchChapters(); // 添加后重新加载章节列表
        });
      }
    }
  },
  mounted() {
    this.fetchChapters();
  }
};
</script>
