(function () {
  'use strict';

  angular.module('northstarApp', [])
    .controller('DashboardController', ['$http', '$q', function ($http, $q) {
      var vm = this;
      vm.projectFilter = 'All';
      vm.query = '';
      vm.projects = [
        {id:'portfolio-insights',name:'Portfolio Insights',type:'FULL-STACK DEMO',category:'Portfolio showcase',status:'Demo ready',statusKey:'live',updated:'Just now',description:'A full-stack portfolio dashboard showing projects, analytics, and activity through one connected UI.',tech:['AngularJS','Django','FastAPI','MongoDB'],theme:'lavender',symbol:'KB',coverLabel:'ONE PROJECT · FOUR STACKS',group:'Product'},
        {id:'atlas',name:'Atlas Workspace',type:'PRODUCT',category:'Productivity',status:'In progress',statusKey:'progress',updated:'2h ago',description:'A calmer command center for teams to plan, align, and move meaningful work forward.',tech:['AngularJS','Django','PostgreSQL'],theme:'lavender',symbol:'A',coverLabel:'PLAN WITH CLARITY',group:'Product'},
        {id:'signal',name:'Signal Metrics',type:'PLATFORM',category:'Data & analytics',status:'Live',statusKey:'live',updated:'Yesterday',description:'Turn product signals into a focused view of what is changing and why it matters.',tech:['FastAPI','MongoDB','Python'],theme:'peach',symbol:'S',coverLabel:'FIND THE SIGNAL',group:'Platform'},
        {id:'fieldnotes',name:'Fieldnotes',type:'EXPERIMENT',category:'Knowledge',status:'In progress',statusKey:'progress',updated:'3 days ago',description:'A lightweight research library that keeps observations connected to decisions.',tech:['AngularJS','FastAPI','MongoDB'],theme:'mint',symbol:'F',coverLabel:'NOTICE MORE',group:'Experiment'},
        {id:'commons',name:'Commons API',type:'PLATFORM',category:'Developer tools',status:'Live',statusKey:'live',updated:'1 week ago',description:'A dependable content service for reusable profiles, projects, and public stories.',tech:['Django','REST API','PostgreSQL'],theme:'blue',symbol:'C',coverLabel:'BUILD IN COMMON',group:'Platform'},
        {id:'goodhours',name:'Good Hours',type:'PRODUCT',category:'Wellbeing',status:'Exploring',statusKey:'exploring',updated:'2 weeks ago',description:'A small experiment in helping people protect time for deep, satisfying work.',tech:['AngularJS','Django','Python'],theme:'rose',symbol:'G',coverLabel:'MAKE SPACE',group:'Product'},
        {id:'pocketlab',name:'Pocket Lab',type:'EXPERIMENT',category:'Prototyping',status:'Exploring',statusKey:'exploring',updated:'3 weeks ago',description:'A set of tiny data stories designed to make everyday systems easier to see.',tech:['FastAPI','MongoDB','D3.js'],theme:'yellow',symbol:'P',coverLabel:'TEST A HUNCH',group:'Experiment'}
      ];
      vm.summary = {activeProjects:1, shipped:1, apiRequests:'24.8', availability:'99.9'};
      vm.activity = [
        {id:1,actor:'You',action:'shipped an update to',target:'Signal Metrics',detail:'Analytics API · v1.4.2',time:'12 min ago',icon:'↗',tone:'orange'},
        {id:2,actor:'Atlas Workspace',action:'completed its',target:'design review',detail:'Milestone · Sprint 08',time:'1 hour ago',icon:'✳',tone:'violet'},
        {id:3,actor:'You',action:'added a new',target:'Fieldnotes collection',detail:'Research · 12 entries',time:'Yesterday',icon:'＋',tone:'green'},
        {id:4,actor:'Commons API',action:'reached',target:'10k requests',detail:'Milestone · All systems healthy',time:'Yesterday',icon:'◎',tone:'blue'}
      ];
      vm.setFilter = function (filter) { vm.projectFilter = filter; };
      Object.defineProperty(vm, 'filteredProjects', {get: function () {
        var q = (vm.query || '').toLowerCase();
        return vm.projects.filter(function (project) {
          return (vm.projectFilter === 'All' || project.group === vm.projectFilter) &&
            (!q || (project.name + ' ' + project.description + ' ' + project.tech.join(' ')).toLowerCase().indexOf(q) >= 0);
        });
      }});

      if (window.DEMO_API_MODE) {
        $q.when(import('https://esm.sh/@apollo/client@3.13.8/core?bundle')).then(function (Apollo) {
          var client = new Apollo.ApolloClient({
            link: new Apollo.HttpLink({ uri: 'http://localhost:8002/graphql' }),
            cache: new Apollo.InMemoryCache()
          });
          return client.query({
            query: Apollo.gql`query PortfolioDashboard { projects { id name type group category status statusKey updated description tech theme symbol coverLabel } summary { activeProjects shipped apiRequests availability } activity { id actor action target detail time icon tone } }`,
            fetchPolicy: 'network-only'
          });
        }).then(function (result) {
          if (result.data.projects.length) vm.projects = result.data.projects;
          angular.extend(vm.summary, result.data.summary);
          if (result.data.activity.length) vm.activity = result.data.activity;
        }).catch(function () { console.info('Using built-in sample data; Apollo Client or the GraphQL gateway is unavailable.'); });
      }
    }]);
}());
