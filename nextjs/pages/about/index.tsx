import React from "react";
import HeaderEvaluator, { MenuItem } from "../../components/HeaderEvaluator";
import { UserCardImage } from "../../components/PersonCard";
import { Center, Group } from "@mantine/core";

const AboutPage = () => {
  return (
    <>
      <HeaderEvaluator activeTab={MenuItem.About} />
      <Center>
        <Group pt={100}>
          <UserCardImage
            avatar=""
            name="Kains"
            job="Data Scientist ESG"
            twitterHandle=""
            githubHandle=""
          />
          <UserCardImage
            avatar=""
            name="Kunal"
            job="Lead Data Scientist ESG"
            twitterHandle=""
            githubHandle=""
          />
          
        </Group>
      </Center>
    </>
  );
};
export default AboutPage;
