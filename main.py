import tls_client, uuid, sys, json


class Linkvertise:
    def __init__(self, url: str) -> None:
        self.session = tls_client.Session(
            client_identifier="chrome_120", random_tls_extension_order=True
        )  # cloudflare "bypass"

        self.endpoint = "https://publisher.linkvertise.com/graphql"
        self.session.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "accept": "application/json",
            "accept-language": "de,en-US;q=0.7,en;q=0.3",
            "accept-encoding": "gzip, deflate, br, zstd",
            "referer": "https://linkvertise.com/",
            "content-type": "application/json",
            "origin": "https://linkvertise.com",
            "connection": "keep-alive",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "priority": "u=0",
        }

        self.url = url
        self.userID = self.url.split("/")[3]
        self.urlName = self.url.split("/")[4]

        self.userIdAndUrl = {"user_id": self.userID, "url": self.urlName}

    @staticmethod
    def action_id_generator():
        result = ""
        for _ in range(3):
            result += str(uuid.uuid4())
        return result[:100]

    def get_user_id(self, linkvertiseUT: str) -> str:
        headers = {
            "connection": "keep-alive",
            "sec-ch-ua-platform": "\"Windows\"",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "accept": "application/json",
            "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
            "sec-ch-ua-mobile": "?0",
            "origin": "https://linkvertise.com",
            "sec-fetch-site": "cross-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://linkvertise.com/",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9"
        }

        querystring = {
            "app.type": "desktop",
            "app.apikey": "5f560f57763908a1256447e08a287e0aaa466fb6",
            "X-Linkvertise-UT": linkvertiseUT
        }

        response = self.session.get("https://api.taboola.com/2.0/json/linkvertise-linkvertiseapikey/user.sync",
                                    headers=headers, params=querystring)
        return response.json()["user"]["id"]

    def getToken(self) -> str:
        try:
            url = "https://publisher.linkvertise.com/api/v1/account"

            response = self.session.get(url)
            print(response.json())
            return response.json()["user_token"]
        except json.decoder.JSONDecodeError:
            print("[-] You're probably ratelimited. Try again in 30s-5m")
            exit()

    def getDetailPageContent(self, linkvertiseUT: str) -> (str, str):
        querystring = {"X-Linkvertise-UT": linkvertiseUT}
        payload = {
            "operationName": "getDetailPageContent",
            "variables": {
                "linkIdentificationInput": {"userIdAndUrl": self.userIdAndUrl},
                "additional_data": {
                    "taboola": {
                        "user_id": self.get_user_id(linkvertiseUT),
                        "url": self.url,
                        "test_group": "old",
                    }
                },
            },
            "query": "mutation getDetailPageContent($linkIdentificationInput: PublicLinkIdentificationInput!, $origin: String, $additional_data: CustomAdOfferProviderAdditionalData!) {\n  getDetailPageContent(\n    linkIdentificationInput: $linkIdentificationInput\n    origin: $origin\n    additional_data: $additional_data\n  ) {\n    access_token\n    payload_bag {\n      taboola {\n        session_id\n        __typename\n      }\n      __typename\n    }\n    premium_subscription_active\n    link {\n      id\n      video_url\n      short_link_title\n      recently_edited\n      short_link_title\n      description\n      url\n      seo_faqs {\n        body\n        title\n        __typename\n      }\n      target_host\n      last_edit_at\n      link_images {\n        url\n        __typename\n      }\n      title\n      thumbnail_url\n      view_count\n      is_trending\n      recently_edited\n      seo_faqs {\n        title\n        body\n        __typename\n      }\n      percentage_rating\n      is_premium_only_link\n      publisher {\n        id\n        name\n        subscriber_count\n        __typename\n      }\n      positive_rating\n      negative_rating\n      already_rated_by_user\n      user_rating\n      __typename\n    }\n    linkCustomAdOffers {\n      title\n      call_to_action\n      description\n      countdown\n      completion_token\n      provider\n      provider_additional_payload {\n        taboola {\n          available_event_url\n          visible_event_url\n          __typename\n        }\n        __typename\n      }\n      media {\n        type\n        ... on UrlMediaResource {\n          content_type\n          resource_url\n          __typename\n        }\n        __typename\n      }\n      clickout_action {\n        type\n        ... on CustomAdOfferClickoutUrlAction {\n          type\n          clickout_url\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    link_recommendations {\n      short_link_title\n      target_host\n      id\n      url\n      publisher {\n        id\n        name\n        __typename\n      }\n      last_edit_at\n      link_images {\n        url\n        __typename\n      }\n      title\n      thumbnail_url\n      view_count\n      is_trending\n      recently_edited\n      percentage_rating\n      publisher {\n        name\n        __typename\n      }\n      __typename\n    }\n    target_access_information {\n      remaining_waiting_time\n      __typename\n    }\n    __typename\n  }\n}",
        }

        response = self.session.post(self.endpoint, json=payload, params=querystring)

        return response.json()["data"]["getDetailPageContent"]["access_token"], \
            response.json()["data"]["getDetailPageContent"]["linkCustomAdOffers"][0]["completion_token"]

    def completeDetailPageContent(self, linkvertiseUT: str, token: str) -> (str, str):
        querystring = {"X-Linkvertise-UT": linkvertiseUT}
        payload = {
            "operationName": "completeDetailPageContent",
            "variables": {
                "linkIdentificationInput": {
                    "userIdAndUrl": self.userIdAndUrl
                },
                "completeDetailPageContentInput": {
                    "access_token": token
                },
            },
            "query": "mutation completeDetailPageContent($linkIdentificationInput: PublicLinkIdentificationInput!, $completeDetailPageContentInput: CompleteDetailPageContentInput!) {\n  completeDetailPageContent(\n    linkIdentificationInput: $linkIdentificationInput\n    completeDetailPageContentInput: $completeDetailPageContentInput\n  ) {\n    CUSTOM_AD_STEP\n    TARGET\n    additional_target_access_information {\n      remaining_waiting_time\n      can_not_access\n      should_show_ads\n      has_long_paywall_duration\n      __typename\n    }\n    __typename\n  }\n}",
        }

        response = self.session.post(self.endpoint, json=payload, params=querystring)

        return response.json()["data"]["completeDetailPageContent"]["CUSTOM_AD_STEP"], \
            response.json()["data"]["completeDetailPageContent"]["TARGET"]

    def completeCustomAdOffer(self, linkvertiseUT: str, completion_token: str, traffic_validation_token: str) -> None:
        querystring = {"X-Linkvertise-UT": linkvertiseUT}
        payload = {
            "operationName": "completeCustomAdOffer",
            "variables": {
                "completion_token": completion_token,
                "traffic_validation_token": traffic_validation_token,
                "action_id": Linkvertise.action_id_generator()
            },
            "query": "mutation completeCustomAdOffer($completion_token: String!, $traffic_validation_token: String!, $action_id: String) {\n  completeCustomAdOffer(\n    completion_token: $completion_token\n    traffic_validation_token: $traffic_validation_token\n    action_id: $action_id\n  )\n}"
        }

        response = self.session.post(self.endpoint, json=payload, params=querystring)
        print(response.text)

    def getDetailPageTarget(self, linkvertiseUT: str, token: str) -> str:
        querystring = {"X-Linkvertise-UT": linkvertiseUT}
        payload = {
            "operationName": "getDetailPageTarget",
            "variables": {
                "linkIdentificationInput": {
                    "userIdAndUrl": self.userIdAndUrl
                },
                "token": token,
            },
            "query": "mutation getDetailPageTarget($linkIdentificationInput: PublicLinkIdentificationInput!, $token: String!, $action_id: String) {\n  getDetailPageTarget(\n    linkIdentificationInput: $linkIdentificationInput\n    token: $token\n    action_id: $action_id\n  ) {\n    type\n    url\n    paste\n    short_link_title\n    __typename\n  }\n}",
        }

        response = self.session.post(self.endpoint, json=payload, params=querystring)
        print(response.text)
        data = response.json()["data"]["getDetailPageTarget"]

        if data["type"] == "URL":
            return data["url"]

        print(data)
        raise NotImplementedError("This Linkvertise type is not implemented yet")

    def __call__(self) -> str:
        linkvertiseUT = self.getToken()
        token, completion_token = self.getDetailPageContent(linkvertiseUT)
        ad_step, token = self.completeDetailPageContent(linkvertiseUT, token)
        self.completeCustomAdOffer(linkvertiseUT, token, ad_step)
        result = self.getDetailPageTarget(linkvertiseUT, token)

        return result


if __name__ == "__main__":
    if len(sys.argv) == 2:
        res = Linkvertise(url=sys.argv[1])()
    else:
        link = input("[?] Input Linkvertise URL >>> ")
        res = Linkvertise(url=link)()

    print("[+]", res)
