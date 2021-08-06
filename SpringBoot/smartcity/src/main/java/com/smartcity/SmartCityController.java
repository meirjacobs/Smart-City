package com.smartcity;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.core.env.Environment;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.ui.Model;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;
import reactor.core.publisher.Mono;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.Arrays;
import java.util.Base64;
import java.util.List;


@org.springframework.stereotype.Controller
public class SmartCityController implements CommandLineRunner {

    @Autowired
    private Environment env;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @GetMapping("/")
    public String getHomePage() {
        return "HomePage";
    }

    public class GetLogin {
        private String username;
        private String password;

        public String getUsername(){ return username;}

        public void setUsername(String username) {this.username = username;}

        public String getPassword(){ return password;}

        public void setPassword(String password) { this.password = password;}
    }

    public class GetData {
        private String id;
        private String problemType;
        private String distance;
        private String latitude;
        private String longitude;
        private String problemDescription;
        private String status;
        private String startTime;
        private String endTime;

        public String getId() {
            return id;
        }

        public void setId(String id) {
            this.id = id;
        }

        public String getProblemType() {
            return problemType;
        }

        public void setProblemType(String problemType) {
            this.problemType = problemType;
        }

        public String getDistance() {
            return distance;
        }

        public void setDistance(String distance) {
            this.distance = distance;
        }

        public String getLatitude() {
            return latitude;
        }

        public void setLatitude(String latitude) {
            this.latitude = latitude;
        }

        public String getLongitude() {
            return longitude;
        }

        public void setLongitude(String longitude) {
            this.longitude = longitude;
        }

        public String getProblemDescription() {
            return problemDescription;
        }

        public void setProblemDescription(String problemDescription) {
            this.problemDescription = problemDescription;
        }

        public String getStatus() {
            return status;
        }

        public void setStatus(String status) {
            this.status = status;
        }

        public String getStartTime() {
            return startTime;
        }

        public void setStartTime(String startTime) {
            this.startTime = startTime;
        }

        public String getEndTime() {
            return endTime;
        }

        public void setEndTime(String endTime) {
            this.endTime = endTime;
        }
    }

    @PostMapping("/employee")
    public String employeeUpdate(@RequestParam("id") int id, @RequestParam("status") String status,@RequestParam("employee_id") String employee_id_str) throws IOException {
        int employee_id = Integer.parseInt(employee_id_str);
        String bodyString = String.format("{\"id\":%d,\"current_status\":\""+status+"\",\"employee_id\":%d}",id,employee_id);
        WebClient client = WebClient.create(env.getProperty("apiURL"));
        WebClient.UriSpec<WebClient.RequestBodySpec> uriSpec = client.put();
        WebClient.RequestBodySpec bodySpec = uriSpec.uri("/");
        WebClient.RequestHeadersSpec<?> headersSpec = bodySpec.bodyValue(bodyString);
        Mono<String> resp = headersSpec.exchangeToMono(response -> {
            return response.bodyToMono(String.class);
        });
        resp.subscribe(System.out::println);
        return "EmployeeThankYou";
    }

    @PostMapping("/report")
    public String handleFileUpload(@RequestParam("image") MultipartFile[] files, @RequestParam("problemType") String problemType,
                                   @RequestParam("latitude") String latitude, @RequestParam("longitude") String longitude,
                                   @RequestParam("problemDescription") String problemDescription) throws IOException {

        WebClient client = WebClient.create(env.getProperty("apiURL"));
        WebClient.UriSpec<WebClient.RequestBodySpec> uriSpec = client.post();
        WebClient.RequestBodySpec bodySpec = uriSpec.uri("/");

        StringBuilder fileString = new StringBuilder();
        for (int i = 0; i < files.length; i++) {
            fileString.append("\"");
            fileString.append(Base64.getEncoder().encodeToString(files[i].getBytes()));
            fileString.append("\"");
            if (files.length != 1 && i != files.length - 1) {
                fileString.append(",");
            }
        }

        String bodyString = "{\"problem_type\":\""+problemType+"\",\"location\":["+latitude+","+longitude+"],\"problem_description\":\""+problemDescription+"\",\"image_path\":["+fileString+"]}";

        WebClient.RequestHeadersSpec<?> headersSpec = bodySpec.bodyValue(bodyString);
        Mono<String> resp = headersSpec.exchangeToMono(response -> {
            if (response.statusCode()
                    .equals(HttpStatus.OK)) {
                return response.bodyToMono(String.class);
            } else if (response.statusCode()
                    .is4xxClientError()) {
                return Mono.just("Error response");
            } else {
                return response.createException()
                        .flatMap(Mono::error);
            }
        });
        resp.subscribe(System.out::println);

        return "ThankYouPage";
    }

    @Override
    public void run(String... args) throws Exception {
        //System.out.println("running");
    }

    @PostMapping("/login")
    public String submitLogin(@ModelAttribute("data") GetLogin body, RedirectAttributes redirectAttributes) {
        // need id, first_name,last_name, department, current_assignment_id
        String username = body.getUsername();
        String password = body.getPassword();
        String employee_idQuery = "Select id from employees where email = \"" +username+ "\"  and pwd = \"" +password+ "\"";
        String employee_id = jdbcTemplate.queryForObject(employee_idQuery,String.class);
        String first_nameQuery = "Select first_name from employees where email = \"" +username+ "\"  and pwd = \"" +password+ "\"";
        String first_name = jdbcTemplate.queryForObject(first_nameQuery,String.class);
        String last_nameQuery = "Select last_name from employees where email = \"" +username+ "\"  and pwd = \"" +password+ "\"";
        String last_name = jdbcTemplate.queryForObject(last_nameQuery,String.class);
        String current_statusQuery = "Select current_assignment_id from employees where email = \"" +username+ "\"  and pwd = \"" +password+ "\"";
        String current_status = jdbcTemplate.queryForObject(current_statusQuery,String.class);
        String departmentQuery = "Select department from employees where email = \"" +username+ "\"  and pwd = \"" +password+ "\"";
        String department = jdbcTemplate.queryForObject(departmentQuery,String.class);
        String current_assignment_id = "";
        if (current_status == null) {
            current_status = "Open";
        } else {
            current_assignment_id = current_status;
            current_status = "Busy";
        }

        MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<>();
        queryParams.put("problem_type", Arrays.asList(department));
        if (current_status == "Busy") {
            queryParams.put("current_status", Arrays.asList("In Progress"));
            queryParams.put("id", Arrays.asList(current_assignment_id));
        } else {
            queryParams.put("current_status", Arrays.asList("Open"));
        }
        WebClient client = WebClient
                .builder()
                .baseUrl(env.getProperty("apiURL"))
                .build();
        List<String> results = client
                .get()
                .uri(uriBuilder -> uriBuilder
                        .path("/")
                        .queryParams(queryParams)
                        .build())
                .retrieve()
                .bodyToFlux(String.class)
                .collectList()
                .block();

        redirectAttributes.addFlashAttribute("message", results);
        redirectAttributes.addFlashAttribute("first_name", first_name);
        redirectAttributes.addFlashAttribute("last_name", last_name);
        redirectAttributes.addFlashAttribute("current_status", current_status);
        redirectAttributes.addFlashAttribute("department", department);
        redirectAttributes.addFlashAttribute("employee_id", employee_id);
    
        return "redirect:/employee";
    }

    @PostMapping("/find")
    public String submitFind(@ModelAttribute("data") GetData body, RedirectAttributes redirectAttributes) {
        MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<>();
        if (!body.getId().equals("")) {
            queryParams.put("id", Arrays.asList(body.getId()));
        }
        if (!body.getProblemType().equals("Any")) {
            queryParams.put("problem_type", Arrays.asList(body.getProblemType()));
        }
        if (!body.getProblemDescription().equals("")) {
            queryParams.put("problem_description", Arrays.asList(body.getProblemDescription()));
        }
        if (!body.getDistance().equals("") && !body.getLatitude().equals("") && !body.getLongitude().equals("")) {
            queryParams.put("distance", Arrays.asList(body.getDistance()));
            queryParams.put("location", Arrays.asList(body.getLatitude() + "," + body.getLongitude()));
        }
        if (!body.getStatus().equals("Any")) {
            queryParams.put("current_status", Arrays.asList(body.getStatus()));
        }
        if (!body.getStartTime().equals("") && !body.getEndTime().equals("")) {
            queryParams.put("time_found", Arrays.asList(body.getStartTime() + "," + body.getEndTime()));
        }
        WebClient client = WebClient
                .builder()
                .baseUrl(env.getProperty("apiURL"))
                .build();
        List<String> results = client
                .get()
                .uri(uriBuilder -> uriBuilder
                        .path("/")
                        .queryParams(queryParams)
                        .build())
                .retrieve()
                .bodyToFlux(String.class)
                .collectList()
                .block();
        redirectAttributes.addFlashAttribute("message", results);

        return "redirect:/results";
    }

    @GetMapping("/employee")
    public String getEmployeePage(Model model) {
        return "employee";
    }

    @GetMapping("/login")
    public String getLoginPage(Model model) {
        return "login";
    }

    @GetMapping("/results")
    public String getResultsPage() {
        return "SearchResults";
    }

    @GetMapping("/report")
    public String getReportPage(Model model) throws FileNotFoundException {
        return "ReportPage";
    }

    @GetMapping("/find")
    public String getFindPage(Model model) {
        return "FindPage";
    }

    @GetMapping("/thanks")
    public String getThanksPage() {
        return "ThankYouPage";
    }
    @GetMapping("/employeeSuccess")
    public String getEmployeeThanksPage() {
        return "EmployeeThankYou";
    }
}